from abc import ABC, abstractmethod

from src.domain.entities import Review


class ReviewRepository(ABC):
    @abstractmethod
    async def save(self, review: Review) -> Review:
        pass

    @abstractmethod
    async def get_by_id(self, review_id: int) -> Review | None:
        pass

    @abstractmethod
    async def find_by_filter(
        self,
        rating: int | None = None,
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
    ) -> list[Review]:
        pass
