from src.domain.entities import Vote
from src.domain.repositories import VoteRepository


class CreateVoteUseCase:
    def __init__(self, vote_repository: VoteRepository):
        self.vote_repository = vote_repository

    async def execute(self, new_vote: Vote) -> Vote:
        if new_vote is None:
            raise ValueError("O voto não pode ser nulo")

        return await self.vote_repository.save(new_vote)