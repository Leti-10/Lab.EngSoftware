from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.social import NotifyUseCase
from src.application.use_cases.vote import (
    CreateVoteUseCase,
    DeleteVoteUseCase,
    FilterVotesUseCase,
    GetVoteByIdUseCase,
)
from src.domain.entities import User
from src.domain.entities.vote import Vote
from src.domain.enums.enums import EnumNotificationType, EnumVoteTarget
from src.domain.exceptions import VoteAlreadyExistsError
from src.domain.repositories import BookListRepository, BookRepository, VoteRepository
from src.domain.repositories.review_repository import ReviewRepository
from src.domain.repositories.social_repository import (
    NotificationPreferenceRepository,
    NotificationRepository,
)
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import SQLAlchemyVoteRepository
from src.presentation.api.dependencies import (
    get_current_user,
    get_notification_preference_repository,
    get_notification_repository,
    get_review_repository,
)
from src.presentation.api.routes.book_list_router import get_book_list_repository
from src.presentation.api.routes.book_router import get_book_repository, to_response
from src.presentation.api.schemas.book_schema import BookResponseSchema
from src.presentation.api.schemas.vote_schema import (
    CreateVoteSchema,
    VoteResponseSchema,
)

router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
    dependencies=[Depends(get_current_user)],
)


async def get_vote_repository(
    session: AsyncSession = Depends(get_db_context),
    book_list_repository: BookListRepository = Depends(get_book_list_repository),
) -> VoteRepository:
    return SQLAlchemyVoteRepository(session, book_list_repository)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_vote(
    payload: CreateVoteSchema,
    repository: VoteRepository = Depends(get_vote_repository),
    reviews: ReviewRepository = Depends(get_review_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    preferences: NotificationPreferenceRepository = Depends(
        get_notification_preference_repository
    ),
    current_user: User = Depends(get_current_user),
) -> VoteResponseSchema:
    if payload.user_id is not None and payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O user_id deve corresponder ao usuário autenticado.",
        )

    try:
        new_vote = await CreateVoteUseCase(repository).execute(
            Vote(
                status=payload.status,
                target_entity=payload.target_entity,
                target_id=payload.target_id,
                user_id=current_user.id,
            )
        )
        if payload.status == "like" and payload.target_entity == EnumVoteTarget.REVIEW:
            review = await reviews.get_by_id(payload.target_id)
            if review is not None:
                await NotifyUseCase(notifications, preferences).execute(
                    review.user_id,
                    current_user.id,
                    EnumNotificationType.LIKE,
                    review_id=review.id,
                    book_id=review.book_id,
                )
        return VoteResponseSchema.model_validate(new_vote)

    except VoteAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O usuário informado não existe.",
        ) from exc


@router.get("/favorites", response_model=list[BookResponseSchema])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    repository: VoteRepository = Depends(get_vote_repository),
    book_repository: BookRepository = Depends(get_book_repository),
) -> list[BookResponseSchema]:
    votes = await FilterVotesUseCase(repository).execute(
        status="favorite",
        target_type=EnumVoteTarget.BOOK,
        user_id=current_user.id,
    )
    books = []
    for vote in votes:
        book = await book_repository.get_by_id(vote.target_id)
        if book is not None:
            books.append(to_response(book))
    return books


@router.put("/favorites/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_favorite(
    book_id: int,
    current_user: User = Depends(get_current_user),
    repository: VoteRepository = Depends(get_vote_repository),
    book_repository: BookRepository = Depends(get_book_repository),
) -> None:
    book = await book_repository.get_by_id(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado."
        )

    existing = await FilterVotesUseCase(repository).execute(
        target_type=EnumVoteTarget.BOOK,
        user_id=current_user.id,
    )
    existing_vote = next((vote for vote in existing if vote.target_id == book_id), None)
    if existing_vote is not None and existing_vote.status == "favorite":
        return

    try:
        await CreateVoteUseCase(repository).execute(
            Vote(
                id=existing_vote.id if existing_vote is not None else None,
                status="favorite",
                target_entity=EnumVoteTarget.BOOK,
                target_id=book_id,
                user_id=current_user.id,
            )
        )
    except VoteAlreadyExistsError:
        return


@router.delete("/favorites/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    book_id: int,
    current_user: User = Depends(get_current_user),
    repository: VoteRepository = Depends(get_vote_repository),
) -> None:
    await repository.delete_by_target(
        current_user.id, EnumVoteTarget.BOOK, book_id, "favorite"
    )


@router.get("/{vote_id}")
async def get_vote(
    vote_id: int,
    repository: VoteRepository = Depends(get_vote_repository),
    current_user: User = Depends(get_current_user),
) -> VoteResponseSchema:
    vote = await GetVoteByIdUseCase(repository).execute(vote_id)
    if vote is None or vote.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Voto não encontrado."
        )
    return VoteResponseSchema.model_validate(vote)


@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vote(
    vote_id: int,
    repository: VoteRepository = Depends(get_vote_repository),
    current_user: User = Depends(get_current_user),
) -> None:
    vote = await GetVoteByIdUseCase(repository).execute(vote_id)
    if vote is None or vote.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Voto não encontrado."
        )
    deleted = await DeleteVoteUseCase(repository).execute(vote_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Voto não encontrado."
        )


@router.get("", response_model=list[VoteResponseSchema])
async def filter_votes(
    status_filter: str | None = Query(default=None, alias="status", min_length=1),
    user_name: str | None = Query(default=None, min_length=1),
    target_type: EnumVoteTarget | None = None,
    target_name: str | None = Query(default=None, min_length=1),
    repository: VoteRepository = Depends(get_vote_repository),
    current_user: User = Depends(get_current_user),
) -> list[VoteResponseSchema]:
    votes = await FilterVotesUseCase(repository).execute(
        status=status_filter,
        user_name=user_name,
        target_type=target_type,
        target_name=target_name,
        user_id=current_user.id,
    )
    return [VoteResponseSchema.model_validate(vote) for vote in votes]
