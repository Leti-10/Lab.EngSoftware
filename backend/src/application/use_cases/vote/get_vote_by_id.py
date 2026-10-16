from src.domain.entities import Vote
from src.domain.repositories import VoteRepository


class GetVoteByIdUseCase:
    def __init__(self, vote_repository: VoteRepository):
        self.vote_repository = vote_repository

    async def execute(self, vote_id: int) -> Vote | None:
        return await self.vote_repository.get_by_id(vote_id)
