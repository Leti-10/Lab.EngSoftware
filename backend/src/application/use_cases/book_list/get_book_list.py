from src.domain.entities import BookList
from src.domain.exceptions import BookListNotFoundError
from src.domain.repositories import BookListRepository


class GetBookListUseCase:
    def __init__(self, book_list_repository: BookListRepository):
        self.book_list_repository = book_list_repository

    def execute(self, list_id: int, user_id: int) -> BookList:
        book_list = self.book_list_repository.get_by_id(list_id)
        if book_list is None or (book_list.private and book_list.owner != user_id):
            raise BookListNotFoundError(list_id)
        return book_list
