from src.domain.entities import Book
from src.domain.repositories import BookRepository


class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self.id = 0
        self.books: dict[int, Book] = {}

    def save(self, book: Book) -> Book:
        self.books[self.id + 1] = book
        self.id += 1
        return book

    def get_by_id(self, book_id: int) -> Book | None:
        return self.books.get(book_id)

    def get_by_isbn(self, isbn: str) -> Book | None:
        for _, book in self.books.items():
            if book.isbn == isbn:
                return book
        return None

    def find_by_filter(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        theme: str | None = None,
        publisher: str | None = None,
    ) -> list[Book | None]:
        results = []
        for _, book in self.books.items():
            if title and title not in book.title:
                continue
            if author and author not in book.author:
                continue
            if genre and genre not in book.genre:
                continue
            if theme and theme not in book.theme:
                continue
            if publisher and publisher not in book.publisher:
                continue
            results.append(book)
        return results
