from src.domain.exceptions import BookNotFoundError
from src.domain.repositories import BookRepository


class DeleteBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, book_id: int) -> None:
        if not await self.book_repository.delete(book_id):
            raise BookNotFoundError(book_id)
