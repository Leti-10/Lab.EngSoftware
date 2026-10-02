from src.domain.entities import Book
from src.domain.exceptions import BookNotFoundError
from src.domain.repositories import BookRepository


class GetBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, book_id: int) -> Book:
        book = await self.book_repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(book_id)
        return book
