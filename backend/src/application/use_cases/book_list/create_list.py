from logging import getLogger

from src.domain.entities import BookList
from src.domain.repositories import BookListRepository

logger = getLogger(__name__)


class CreateBookListUseCase:
    def __init__(self, book_list_repository: BookListRepository):
        self.book_list_repository = book_list_repository

    async def execute(self, new_book_list: BookList) -> BookList:
        if new_book_list is None:
            raise ValueError("A lista não pode ser nula")

        if await self.book_list_repository.get_by_name(new_book_list.name):
            raise ValueError("Nome da lista já cadastrado")

        new_book_list = await self.book_list_repository.save(new_book_list)

        logger.debug(
            "Creating new book list",
            extra={"list_name": new_book_list.name},
        )

        return new_book_list
