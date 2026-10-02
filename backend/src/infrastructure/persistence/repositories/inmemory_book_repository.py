from src.domain.entities import Book
from src.domain.repositories import BookRepository


class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self.id = 0
        self.books: dict[int, Book] = {}

    async def save(self, book: Book) -> Book:
        id_book = self.id + 1
        book.id = id_book
        self.books[id_book] = book
        self.id += 1
        return book

    async def get_by_id(self, book_id: int) -> Book | None:
        return self.books.get(book_id)

    async def get_by_isbn(self, isbn: str) -> Book | None:
        for _, book in self.books.items():
            if book.isbn == isbn:
                return book
        return None

    async def find_by_filter(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        theme: str | None = None,
        publisher: str | None = None,
    ) -> list[Book | None]:
        def contains(term: str, value: str) -> bool:
            return term.lower() in value.lower()

        def any_contains(term: str, values: list[str] | str) -> bool:
            items = [values] if isinstance(values, str) else values
            return any(contains(term, item) for item in items)

        results = []
        for book in self.books.values():
            if title and not contains(title, book.title):
                continue
            if author and not any_contains(author, book.authors):
                continue
            if genre and not any(genre.lower() == g.lower() for g in book.genre):
                continue
            if theme and not any_contains(theme, book.theme):
                continue
            if publisher and not contains(publisher, book.publisher):
                continue
            results.append(book)
        return results
