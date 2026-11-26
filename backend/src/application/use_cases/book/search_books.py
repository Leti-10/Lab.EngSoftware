from logging import getLogger

from src.domain.entities import Book
from src.domain.repositories import BookRepository


logger = getLogger(__name__)


class SearchBooksUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(
        self,
        query: str | None = None,
        genre: str | None = None,
    ) -> list[Book]:
        query = (query or "").strip() or None
        genre = (genre or "").strip() or None

        if query is None and genre is None:
            find_books = await self.book_repository.get_all()
        else:
            find_books = await self.book_repository.find_by_filter(
                title=query,
                author=query,
                genre=genre or query,
            )

        unique: dict[int, Book] = {}

        if not find_books:
            logger.debug("No books found for query '%s' and genre '%s'", query, genre)
            return []

        for book in find_books:
            if book is not None:
                if book.id is not None:
                    unique[book.id] = book

        return sorted(unique.values(), key=lambda b: b.title.lower())
