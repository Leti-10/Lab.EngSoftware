from logging import getLogger

from src.domain.entities import BookList
from src.domain.exceptions import BookListForbiddenError, BookListNotFoundError
from src.domain.repositories import BookListRepository

logger = getLogger(__name__)


class UpdateBookListUseCase:
    def __init__(self, book_list_repository: BookListRepository):
        self.book_list_repository = book_list_repository

    async def execute(
        self,
        list_id: int,
        user_id: int,
        name: str,
        description: str,
        private: bool,
    ) -> BookList:
        current = await self.book_list_repository.get_by_id(list_id)
        if current is None:
            raise BookListNotFoundError(list_id)
        if current.owner != user_id:
            raise BookListForbiddenError()

        updated = BookList(
            owner=current.owner,
            name=name.strip(),
            description=description.strip(),
            private=private,
            books=list(current.books),
        )
        duplicate = await self.book_list_repository.get_by_name(updated.name)
        if duplicate is not None and duplicate.id != list_id:
            raise ValueError("Nome da lista já cadastrado")

        updated.id = list_id
        saved = await self.book_list_repository.update(updated)
        if saved is None:
            raise BookListNotFoundError(list_id)

        logger.debug(
            "Book list updated successfully",
            extra={"list_id": list_id, "user_id": user_id},
        )
        return saved
