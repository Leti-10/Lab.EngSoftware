from src.domain.entities import Vote
from src.domain.repositories import VoteRepository


class InMemoryVoteRepository(VoteRepository):
    def __init__(self):
        self.votes: dict[int, Vote] = {}
        self._next_id = 1

    async def save(self, vote: Vote) -> Vote:
        if vote.id is None:
            vote.id = self._next_id
            self._next_id += 1
        self.votes[vote.id] = vote
        return vote

    async def get_by_id(self, vote_id: int) -> Vote | None:
        return self.votes.get(vote_id)

    async def find_by_filter(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: str | None = None,
        target_name: str | None = None,
    ) -> list[Vote]:
        raise NotImplementedError("Os filtros de vote dependem das modelagens relacionadas.")