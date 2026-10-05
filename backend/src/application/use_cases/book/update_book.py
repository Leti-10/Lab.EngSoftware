from src.domain.entities import Book
from src.domain.exceptions import BookNotFoundError
from src.domain.repositories import BookRepository


class UpdateBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, book_id: int, updated: Book) -> Book:
        if await self.book_repository.get_by_id(book_id) is None:
            raise BookNotFoundError(book_id)

        same_isbn = await self.book_repository.get_by_isbn(updated.isbn)
        if same_isbn is not None and same_isbn.id != book_id:
            raise ValueError("ISBN já cadastrado")

        updated.id = book_id
        return await self.book_repository.update(updated)
