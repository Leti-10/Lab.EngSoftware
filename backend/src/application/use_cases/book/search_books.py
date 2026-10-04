from src.domain.entities import Book
from src.domain.repositories import BookRepository


class SearchBooksUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, query: str | None = None, genre: str | None = None) -> list[Book]:
        query = (query or "").strip() or None

        if query is None:
            return [b for b in await self.book_repository.find_by_filter(genre=genre) if b]

        by_title = await self.book_repository.find_by_filter(title=query, genre=genre)
        by_author = await self.book_repository.find_by_filter(author=query, genre=genre)

        unique: dict[int, Book] = {}
        for book in [*by_title, *by_author]:
            if book is not None:
                unique[book.id] = book
        return sorted(unique.values(), key=lambda book: book.id)
