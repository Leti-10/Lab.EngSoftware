from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from src.application.use_cases.review import (
    CreateReviewUseCase,
    FilterReviewsUseCase,
    GetReviewByIdUseCase,
    UpdateReviewUseCase,
)
from src.domain.entities import User
from src.domain.entities.review import Review
from src.domain.enums.enums import EnumVoteTarget
from src.domain.exceptions import ReviewAlreadyExistsError, ReviewNotFoundError
from src.domain.repositories import UserRepository, VoteRepository
from src.domain.repositories.review_repository import ReviewRepository
from src.presentation.api.dependencies import (
    get_current_user,
    get_optional_user,
    get_review_repository,
    get_user_repository,
)
from src.presentation.api.routes.vote_router import get_vote_repository
from src.presentation.api.schemas.review_schema import (
    CreateReviewSchema,
    ReviewResponseSchema,
    UpdateReviewSchema,
    UpdateReviewSpoilerSchema,
)

LIKE_STATUS = "like"

router = APIRouter(prefix="/reviews", tags=["Reviews"])


async def build_responses(
    reviews: list[Review],
    users: UserRepository,
    votes: VoteRepository,
    viewer: User | None,
) -> list[ReviewResponseSchema]:
    likes = await votes.find_by_filter(
        status=LIKE_STATUS, target_type=EnumVoteTarget.REVIEW
    )
    like_count: dict[int, int] = {}
    my_likes: dict[int, int | None] = {}
    for vote in likes:
        like_count[vote.target_id] = like_count.get(vote.target_id, 0) + 1
        if viewer is not None and vote.user_id == viewer.id:
            my_likes[vote.target_id] = vote.id

    usernames: dict[int, str | None] = {}
    responses = []
    for review in reviews:
        if review.user_id not in usernames:
            author = await users.get_by_id(review.user_id)
            usernames[review.user_id] = author.username if author else None
        response = ReviewResponseSchema.model_validate(review)
        response.username = usernames[review.user_id]
        response.likes = like_count.get(review.id, 0)
        response.liked_by_me = review.id in my_likes
        response.like_vote_id = my_likes.get(review.id)
        responses.append(response)
    return responses


async def load_review(review_id: int, repository: ReviewRepository) -> Review:
    try:
        return await GetReviewByIdUseCase(repository).execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc


def ensure_owner(review: Review, user: User) -> None:
    if review.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar a sua própria resenha.",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: CreateReviewSchema,
    repository: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    votes: VoteRepository = Depends(get_vote_repository),
    current_user: User = Depends(get_current_user),
) -> ReviewResponseSchema:
    existing = await FilterReviewsUseCase(repository).execute(
        book_id=payload.book_id, user_id=current_user.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ReviewAlreadyExistsError().message,
        )
    try:
        new_review = await CreateReviewUseCase(repository).execute(
            Review(**payload.model_dump(), user_id=current_user.id)
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O usuário informado não existe.",
        ) from exc
    return (await build_responses([new_review], users, votes, current_user))[0]


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    repository: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    votes: VoteRepository = Depends(get_vote_repository),
    viewer: User | None = Depends(get_optional_user),
) -> ReviewResponseSchema:
    review = await load_review(review_id, repository)
    return (await build_responses([review], users, votes, viewer))[0]


@router.put("/{review_id}")
async def update_review(
    review_id: int,
    payload: UpdateReviewSchema,
    repository: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    votes: VoteRepository = Depends(get_vote_repository),
    current_user: User = Depends(get_current_user),
) -> ReviewResponseSchema:
    review = await load_review(review_id, repository)
    ensure_owner(review, current_user)

    updated_review = Review(
        id=review_id,
        rating=payload.rating,
        comment=payload.comment,
        isSpoiler=payload.isSpoiler,
        user_id=review.user_id,
        book_id=review.book_id,
        created_at=review.created_at,
    )
    try:
        updated = await UpdateReviewUseCase(repository).execute(
            review_id, updated_review
        )
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O usuário informado não existe.",
        ) from exc
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review não encontrada."
        )
    return (await build_responses([updated], users, votes, current_user))[0]


@router.patch("/{review_id}/spoiler")
async def update_review_spoiler(
    review_id: int,
    payload: UpdateReviewSpoilerSchema,
    repository: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    votes: VoteRepository = Depends(get_vote_repository),
    current_user: User = Depends(get_current_user),
) -> ReviewResponseSchema:
    review = await load_review(review_id, repository)
    ensure_owner(review, current_user)

    review.isSpoiler = payload.isSpoiler
    try:
        updated = await UpdateReviewUseCase(repository).execute(review_id, review)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc
    return (await build_responses([updated], users, votes, current_user))[0]


@router.get("", response_model=list[ReviewResponseSchema])
async def filter_reviews(
    rating: int | None = Query(default=None, ge=1, le=5),
    username: str | None = Query(default=None, min_length=1),
    book_title: str | None = Query(default=None, min_length=1),
    comment: str | None = None,
    book_id: int | None = Query(default=None, gt=0),
    user_id: int | None = Query(default=None, gt=0),
    repository: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    votes: VoteRepository = Depends(get_vote_repository),
    viewer: User | None = Depends(get_optional_user),
) -> list[ReviewResponseSchema]:
    reviews = await FilterReviewsUseCase(repository).execute(
        rating=rating,
        username=username,
        book_title=book_title,
        comment=comment,
        book_id=book_id,
        user_id=user_id,
    )
    return await build_responses(reviews, users, votes, viewer)
