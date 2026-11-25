from src.domain.entities import Book
from src.domain.repositories import BookRepository


class SearchBooksUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(
        self,
        query: str | None = None,
    ) -> list[Book]:
        query = (query or "").strip() or None

        if query is None:
            return []

        find_books = await self.book_repository.find_by_filter(
            title=query, author=query, genre=query
        )

        unique: dict[int, Book] = {}

        for book in find_books:
            if book is not None:
                if book.id is not None:
                    unique[book.id] = book

        return sorted(unique.values(), key=lambda b: b.title.lower())
