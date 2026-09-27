import pytest

from src.domain.entities import Book


@pytest.fixture
def book_repository():
    from src.infrastructure.persistence.repositories import (
        InMemoryBookRepository,
    )

    return InMemoryBookRepository()


@pytest.fixture
def create_book_use_case(book_repository):
    from src.application.use_cases import CreateBookUseCase

    return CreateBookUseCase(book_repository)


async def test_should_create_book_successfully(create_book_use_case):
    book_data = Book(
        id=1,
        isbn="9788522031429",
        genre=["Ficção", "Romance"],
        theme=["Amor", "Aventura"],
        title="O Pequeno Príncipe",
        authors=["Antoine de Saint-Exupéry"],
        publisher="Editora Agir",
    )

    result = await create_book_use_case.execute(book_data)

    assert book_data == result


async def test_should_raise_error_when_isbn_exists(create_book_use_case):
    book_1 = Book(
        isbn="9788522031429",
        title="Livro de teste 1",
        authors=["Wesley"],
        publisher="Sem editora",
    )

    await create_book_use_case.execute(book_1)

    book_2 = Book(
        isbn="9788522031429",
        title="Livro de teste 2",
        authors=["Wesley"],
        publisher="Sem editora",
    )

    with pytest.raises(ValueError, match="ISBN já cadastrado"):
        await create_book_use_case.execute(book_2)
