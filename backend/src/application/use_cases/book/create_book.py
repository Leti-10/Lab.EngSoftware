from logging import getLogger

from src.domain.entities import Book
from src.domain.repositories import BookRepository

logger = getLogger(__name__)


class CreateBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, new_book: Book):
        if new_book is None:
            raise ValueError("O livro não pode ser nulo")

        existing_book = await self.book_repository.get_by_isbn(new_book.isbn)

        if existing_book:
            raise ValueError("ISBN já cadastrado")

        saved_book = await self.book_repository.save(new_book)

        logger.info(
            "Book created successfully",
            extra={"book_id": saved_book.id, "isbn": saved_book.isbn},
        )

        return saved_book
