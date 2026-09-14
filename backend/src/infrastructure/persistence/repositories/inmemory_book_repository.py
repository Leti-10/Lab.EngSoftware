from src.domain.entities.book import Book
from src.domain.repositories.book_repository import BookRepository


class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self.books = []

    def save(self, book: Book) -> Book:
        self.books.append(book)
        return book

    def get_by_id(self, book_id: int) -> Book | None:
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def get_by_isbn(self, isbn: str) -> Book | None:
        for book in self.books:
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
        for book in self.books:
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
