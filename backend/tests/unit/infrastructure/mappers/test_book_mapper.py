from src.infrastructure.persistence.mappers import BookMapper
from src.infrastructure.persistence.models import (
    BookModelSQLAlchemy,
    AuthorModelSQLAlchemy,
)
from src.domain.entities import Book


def test_mapper_book_entity_to_model_successfully():
    isbn = "1230001231"
    title = "teste_mapper"
    publisher = "fatec_sjc"
    author = ["unknown"]
    test_book = Book(isbn=isbn, title=title, publisher=publisher, authors=author)

    book_model_test = BookMapper.to_sqlalchemy(test_book)

    assert isinstance(book_model_test, BookModelSQLAlchemy)
    assert book_model_test.isbn == isbn
    assert book_model_test.title == title
    assert book_model_test.publisher == publisher


def test_mapper_book_model_to_entity_successfully():
    isbn = "1230001231"
    title = "teste_mapper"
    publisher = "fatec_sjc"
    author = ["unknow"]

    test_book_model = BookModelSQLAlchemy(
        isbn=isbn,
        title=title,
        publisher=publisher,
        authors=[AuthorModelSQLAlchemy(name=name) for name in author],
    )

    test_book = BookMapper.to_domain(test_book_model)

    assert isinstance(test_book, Book)
    assert test_book.isbn == isbn
    assert test_book.title == title
    assert test_book.publisher == publisher
