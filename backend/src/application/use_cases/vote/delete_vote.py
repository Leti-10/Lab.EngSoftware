from src.domain.repositories import VoteRepository


class DeleteVoteUseCase:
    def __init__(self, vote_repository: VoteRepository):
        self.vote_repository = vote_repository

    async def execute(self, vote_id: int) -> bool:
        return await self.vote_repository.delete(vote_id)
