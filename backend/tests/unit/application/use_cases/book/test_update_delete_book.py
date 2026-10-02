import pytest

from src.application.use_cases import (
    CreateBookUseCase,
    DeleteBookUseCase,
    UpdateBookUseCase,
)
from src.domain.entities import Book
from src.domain.exceptions import BookNotFoundError
from src.infrastructure.persistence.repositories import InMemoryBookRepository


def make_book(isbn="9788542603835", title="One Piece"):
    return Book(
        isbn=isbn,
        title=title,
        authors=["Eiichiro Oda"],
        publisher="Panini",
        genre=["Mangá"],
    )


@pytest.fixture
async def repository():
    repo = InMemoryBookRepository()
    create = CreateBookUseCase(repo)
    await create.execute(make_book())
    await create.execute(make_book(isbn="9788535902778", title="Dom Casmurro"))
    return repo


async def test_should_update_book(repository):
    updated = await UpdateBookUseCase(repository).execute(1, make_book(title="One Piece 2"))

    assert updated.id == 1
    assert (await repository.get_by_id(1)).title == "One Piece 2"


async def test_should_allow_keeping_the_same_isbn(repository):
    updated = await UpdateBookUseCase(repository).execute(1, make_book())

    assert updated.isbn == "9788542603835"


async def test_should_reject_isbn_used_by_another_book(repository):
    with pytest.raises(ValueError, match="ISBN já cadastrado"):
        await UpdateBookUseCase(repository).execute(1, make_book(isbn="9788535902778"))


async def test_should_fail_to_update_unknown_book(repository):
    with pytest.raises(BookNotFoundError):
        await UpdateBookUseCase(repository).execute(99, make_book())


async def test_should_delete_book(repository):
    await DeleteBookUseCase(repository).execute(1)

    assert await repository.get_by_id(1) is None
    assert await repository.get_by_id(2) is not None


async def test_should_fail_to_delete_unknown_book(repository):
    with pytest.raises(BookNotFoundError):
        await DeleteBookUseCase(repository).execute(99)
