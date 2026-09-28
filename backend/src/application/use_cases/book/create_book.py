from src.domain.entities import Book
from src.domain.repositories import BookRepository


class CreateBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    async def execute(self, new_book: Book):
        if new_book is None:
            raise ValueError("O livro não pode ser nulo")

        if await self.book_repository.get_by_isbn(new_book.isbn):
            raise ValueError("ISBN já cadastrado")
        else:
            print(await self.book_repository.get_by_isbn(new_book.isbn))

        return await self.book_repository.save(new_book)
