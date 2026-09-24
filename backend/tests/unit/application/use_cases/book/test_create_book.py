import pytest

from src.domain.entities.book import Book


@pytest.fixture
def book_repository():
    from src.infrastructure.persistence.repositories.inmemory_book_repository import (
        InMemoryBookRepository,
    )

    return InMemoryBookRepository()


@pytest.fixture
def create_book_use_case(book_repository):
    from src.application.use_cases.book.create_book import CreateBookUseCase

    return CreateBookUseCase(book_repository)


def test_should_create_book_successfully(create_book_use_case):
    book_data = Book(
        isbn="9788522031429",
        genre=["Ficção", "Romance"],
        theme=["Amor", "Aventura"],
        title="O Pequeno Príncipe",
        author=["Antoine de Saint-Exupéry"],
        publisher="Editora Agir",
    )

    result = create_book_use_case.execute(book_data)

    assert book_data == result


def test_should_raise_error_when_isbn_exists(create_book_use_case):
    book_1 = Book(
        isbn="9788522031429",
        title="Livro de teste 1",
        author=["Wesley"],
        publisher="Sem editora",
    )

    create_book_use_case.execute(book_1)

    book_2 = Book(
        isbn="9788522031429",
        title="Livro de teste 2",
        author=["Wesley"],
        publisher="Sem editora",
    )

    with pytest.raises(ValueError, match="ISBN já cadastrado"):
        create_book_use_case.execute(book_2)
