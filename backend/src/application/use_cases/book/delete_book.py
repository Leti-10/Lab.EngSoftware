from logging import getLogger

from src.domain.exceptions import BookNotFoundError
from src.domain.repositories import BookRepository

logger = getLogger(__name__)


class DeleteBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, book_id: int) -> None:
        if not await self.book_repository.delete(book_id):
            raise BookNotFoundError(book_id)

        logger.info(
            "Book deleted successfully",
            extra={"book_id": book_id},
        )
