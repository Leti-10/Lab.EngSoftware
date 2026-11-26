from abc import ABC, abstractmethod

from src.domain.entities import Review
from src.domain.enums.enums import EnumReviewSort


class ReviewRepository(ABC):
    @abstractmethod
    async def save(self, review: Review) -> Review:
        pass

    @abstractmethod
    async def update(self, review: Review) -> Review | None:
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
        book_id: int | None = None,
        user_id: int | None = None,
    ) -> list[Review | None]:
        pass

    @abstractmethod
    async def get_all(self, order_by: str = "id") -> list[Review]:
        pass

    @abstractmethod
    async def get_page(
        self, page: int, page_size: int, sort_by: EnumReviewSort
    ) -> tuple[list[Review], int]:
        pass
