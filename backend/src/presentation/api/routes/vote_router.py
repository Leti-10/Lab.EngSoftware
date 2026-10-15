from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.vote import (
    CreateVoteUseCase,
    DeleteVoteUseCase,
    FilterVotesUseCase,
    GetVoteByIdUseCase,
)
from src.domain.entities import User
from src.domain.entities.vote import Vote
from src.domain.enums.enums import VoteTarget
from src.domain.repositories import BookListRepository, VoteRepository
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import SQLAlchemyVoteRepository
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.routes.book_list_router import get_book_list_repository
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
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O usuário informado não existe.",
        ) from exc
    return VoteResponseSchema.model_validate(new_vote)


@router.get("/{vote_id}")
async def get_vote(
    vote_id: int,
    repository: VoteRepository = Depends(get_vote_repository),
) -> VoteResponseSchema:
    vote = await GetVoteByIdUseCase(repository).execute(vote_id)
    if vote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Voto não encontrado."
        )
    return VoteResponseSchema.model_validate(vote)


@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vote(
    vote_id: int,
    repository: VoteRepository = Depends(get_vote_repository),
) -> None:
    deleted = await DeleteVoteUseCase(repository).execute(vote_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Voto não encontrado."
        )


@router.get("", response_model=list[VoteResponseSchema])
async def filter_votes(
    status_filter: str | None = Query(default=None, alias="status", min_length=1),
    user_name: str | None = Query(default=None, min_length=1),
    target_type: VoteTarget | None = None,
    target_name: str | None = Query(default=None, min_length=1),
    repository: VoteRepository = Depends(get_vote_repository),
) -> list[VoteResponseSchema]:
    votes = await FilterVotesUseCase(repository).execute(
        status=status_filter,
        user_name=user_name,
        target_type=target_type,
        target_name=target_name,
    )
    return [VoteResponseSchema.model_validate(vote) for vote in votes]
