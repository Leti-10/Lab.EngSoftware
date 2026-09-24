from abc import ABC, abstractmethod
from src.domain.entities import Book


class BookRepository(ABC):
    @abstractmethod
    def save(self, book: Book) -> Book:
        pass

    @abstractmethod
    def get_by_id(self, book_id: int) -> Book | None:
        pass

    @abstractmethod
    def get_by_isbn(self, isbn: str) -> Book | None:
        pass

    @abstractmethod
    def find_by_filter(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        theme: str | None = None,
        publisher: str | None = None,
    ) -> list[Book | None]:
        pass
