from abc import ABC, abstractmethod

from src.domain.entities import Vote
from src.domain.enums.enums import VoteTarget


class VoteRepository(ABC):
    @abstractmethod
    async def save(self, vote: Vote) -> Vote:
        pass

    @abstractmethod
    async def get_by_id(self, vote_id: int) -> Vote | None:
        pass

    @abstractmethod
    async def find_by_filter(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: VoteTarget | None = None,
        target_name: str | None = None,
    ) -> list[Vote]:
        pass