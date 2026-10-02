from src.domain.entities import BookList
from src.domain.exceptions import (
    BookAlreadyInListError,
    BookListForbiddenError,
    BookListNotFoundError,
    BookNotFoundError,
)
from src.domain.repositories import BookListRepository, BookRepository


class AddBookToListUseCase:
    def __init__(
        self, book_list_repository: BookListRepository, book_repository: BookRepository
    ):
        self.book_list_repository = book_list_repository
        self.book_repository = book_repository

    async def execute(self, list_id: int, book_id: int, user_id: int) -> BookList:
        book_list = self.book_list_repository.get_by_id(list_id)
        if book_list is None:
            raise BookListNotFoundError(list_id)
        if book_list.owner != user_id:
            raise BookListForbiddenError()
        if await self.book_repository.get_by_id(book_id) is None:
            raise BookNotFoundError(book_id)
        if book_id in book_list.books:
            raise BookAlreadyInListError()

        book_list.books.append(book_id)
        return book_list
