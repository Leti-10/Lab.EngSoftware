from abc import ABC, abstractmethod
from src.domain.entities import BookList


class BookListRepository(ABC):
    @abstractmethod
    async def save(self, book_list: BookList) -> BookList:
        pass

    @abstractmethod
    async def update(self, book_list: BookList) -> BookList | None:
        pass

    @abstractmethod
    async def get_by_id(self, list_id: int) -> BookList | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> BookList | None:
        pass

    @abstractmethod
    async def delete(self, list_id: int) -> bool:
        pass

    @abstractmethod
    async def list_by_owner(self, owner_id: int) -> list[BookList]:
        pass
