from abc import ABC, abstractmethod
from src.domain.entities import BookList


class BookListRepository(ABC):
    @abstractmethod
    def save(self, book_list: BookList) -> BookList:
        pass

    @abstractmethod
    def get_by_id(self, list_id: int) -> BookList | None:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> BookList | None:
        pass

    @abstractmethod
    def delete(self, list_id: int) -> bool:
        pass
