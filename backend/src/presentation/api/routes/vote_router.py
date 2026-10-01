from fastapi import APIRouter, Depends, status

from src.application.use_cases.vote.create_vote import CreateVoteUseCase
from src.domain.entities.vote import Vote
from src.domain.repositories.vote_repository import VoteRepository
from src.infrastructure.persistence.repositories.inmemory_vote_repository import (
    InMemoryVoteRepository,
)
from src.presentation.api.schemas.vote_schema import CreateVoteSchema

router = APIRouter(prefix="/votes", tags=["Votes"])

in_memory_repo_instance = InMemoryVoteRepository()


def get_vote_repository() -> VoteRepository:
    return in_memory_repo_instance


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_vote(
    payload: CreateVoteSchema,
    repository: VoteRepository = Depends(get_vote_repository),
):
    try:
        use_case = CreateVoteUseCase(repository)
        new_vote = await use_case.execute(Vote(**payload.model_dump()))
        return new_vote
    except Exception as exc:
        return exc


@router.get("/{vote_id}")
async def get_vote(vote_id: int):
    return {"vote_id": vote_id}
