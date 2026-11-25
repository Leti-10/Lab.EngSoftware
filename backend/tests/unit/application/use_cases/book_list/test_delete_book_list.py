import pytest


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


async def test_should_delete_book_list_successfully(book_list_repository):
    from src.application.use_cases import DeleteBookListUseCase
    from src.domain.entities import BookList

    book_list = BookList(
        owner=1,
        name="Minhas leituras",
        description="Lista de livros favoritos",
        private=True,
        books=[1, 2, 3],
    )

    book_list_repository.save(book_list)

    delete_book_list_use_case = DeleteBookListUseCase(book_list_repository)

    await delete_book_list_use_case.execute(book_list.id, book_list.owner)

    assert book_list_repository.get_by_id(book_list.id) is None