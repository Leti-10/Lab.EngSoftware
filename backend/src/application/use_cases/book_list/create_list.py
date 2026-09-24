from src.domain.entities import BookList
from src.domain.repositories import BookListRepository


class CreateBookListUseCase:
    def __init__(self, book_list_repository: BookListRepository):
        self.book_list_repository = book_list_repository

    def execute(self, new_book_list: BookList):
        if new_book_list is None:
            raise ValueError("A lista não pode ser nula")

        if self.book_list_repository.get_by_name(new_book_list.name):
            raise ValueError("Nome da lista já cadastrado")

        return self.book_list_repository.save(new_book_list)
