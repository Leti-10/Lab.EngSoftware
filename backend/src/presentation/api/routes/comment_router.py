from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.social import (
    AddCommentUseCase,
    DeleteCommentUseCase,
    ListCommentsUseCase,
    NotifyUseCase,
)
from src.domain.entities import User
from src.domain.entities.social import Comment
from src.domain.enums.enums import EnumNotificationType
from src.domain.exceptions import (
    CommentForbiddenError,
    CommentNotFoundError,
    InvalidCommentError,
)
from src.domain.repositories import UserRepository
from src.domain.repositories.review_repository import ReviewRepository
from src.domain.repositories.social_repository import (
    CommentRepository,
    NotificationPreferenceRepository,
    NotificationRepository,
)
from src.presentation.api.dependencies import (
    get_comment_repository,
    get_current_user,
    get_notification_preference_repository,
    get_notification_repository,
    get_review_repository,
    get_user_repository,
)
from src.presentation.api.schemas.social_schema import (
    CommentResponseSchema,
    CreateCommentSchema,
)

router = APIRouter(tags=["Comments"])


async def _to_responses(
    comments: list[Comment], users: UserRepository
) -> list[CommentResponseSchema]:
    names: dict[int, str | None] = {}
    responses = []
    for comment in comments:
        if comment.user_id not in names:
            author = await users.get_by_id(comment.user_id)
            names[comment.user_id] = author.username if author else None
        responses.append(
            CommentResponseSchema(
                id=comment.id,
                review_id=comment.review_id,
                user_id=comment.user_id,
                username=names[comment.user_id],
                text=comment.text,
                created_at=comment.created_at,
            )
        )
    return responses


async def _require_review(review_id: int, reviews: ReviewRepository):
    review = await reviews.get_by_id(review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resenha não encontrada."
        )
    return review


@router.get("/reviews/{review_id}/comments")
async def list_comments(
    review_id: int,
    comments: CommentRepository = Depends(get_comment_repository),
    reviews: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
) -> list[CommentResponseSchema]:
    await _require_review(review_id, reviews)
    found = await ListCommentsUseCase(comments).execute(review_id)
    return await _to_responses(found, users)


@router.post("/reviews/{review_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    review_id: int,
    payload: CreateCommentSchema,
    comments: CommentRepository = Depends(get_comment_repository),
    reviews: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    preferences: NotificationPreferenceRepository = Depends(
        get_notification_preference_repository
    ),
    current_user: User = Depends(get_current_user),
) -> CommentResponseSchema:
    review = await _require_review(review_id, reviews)
    try:
        comment = await AddCommentUseCase(comments).execute(
            review_id, current_user.id, payload.text
        )
    except InvalidCommentError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.message
        ) from error

    await NotifyUseCase(notifications, preferences).execute(
        review.user_id,
        current_user.id,
        EnumNotificationType.COMMENT,
        review_id=review.id,
        book_id=review.book_id,
    )
    return (await _to_responses([comment], users))[0]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    comments: CommentRepository = Depends(get_comment_repository),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        await DeleteCommentUseCase(comments).execute(comment_id, current_user.id)
    except CommentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.message
        ) from error
    except CommentForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=error.message
        ) from error
