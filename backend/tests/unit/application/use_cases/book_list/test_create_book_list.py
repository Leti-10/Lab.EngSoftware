import pytest

from src.domain.entities import BookList


@pytest.fixture
def book_list_repository():
    from src.infrastructure.persistence.repositories import (
        InMemoryBookListRepository,
    )

    return InMemoryBookListRepository()


@pytest.fixture
def create_book_list_use_case(book_list_repository):
    from src.application.use_cases import CreateBookListUseCase

    return CreateBookListUseCase(book_list_repository)


def test_should_create_book_list_successfully(create_book_list_use_case):
    book_list_data = BookList(
        owner=1,
        name="Minhas leituras",
        description="Lista de livros favoritos",
        private=True,
        books=[1, 2, 3],
    )

    result = create_book_list_use_case.execute(book_list_data)

    assert book_list_data == result


def test_should_raise_error_when_list_name_exists(create_book_list_use_case):
    book_list_1 = BookList(
        owner=1,
        name="Minhas leituras",
        description="Primeira lista de leitura",
        private=True,
        books=[1],
    )

    create_book_list_use_case.execute(book_list_1)

    book_list_2 = BookList(
        owner=2,
        name="Minhas leituras",
        description="Segunda lista de leitura",
        private=False,
        books=[2],
    )

    with pytest.raises(ValueError, match="Nome da lista já cadastrado"):
        create_book_list_use_case.execute(book_list_2)
