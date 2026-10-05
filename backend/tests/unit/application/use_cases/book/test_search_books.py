import pytest

from src.application.use_cases import CreateBookUseCase, SearchBooksUseCase
from src.domain.entities import Book
from src.infrastructure.persistence.repositories import InMemoryBookRepository


@pytest.fixture
async def repository():
    repo = InMemoryBookRepository()
    create = CreateBookUseCase(repo)
    await create.execute(
        Book(isbn="9788542603835", title="One Piece", authors=["Eiichiro Oda"],
             publisher="Panini", genre=["Mangá", "Aventura"])
    )
    await create.execute(
        Book(isbn="9788535902778", title="Dom Casmurro", authors=["Machado de Assis"],
             publisher="Companhia", genre=["Romance"])
    )
    return repo


async def test_should_list_everything_without_filters(repository):
    books = await SearchBooksUseCase(repository).execute()

    assert [b.title for b in books] == ["One Piece", "Dom Casmurro"]


async def test_should_search_by_title_ignoring_case(repository):
    books = await SearchBooksUseCase(repository).execute(query="casmurro")

    assert [b.title for b in books] == ["Dom Casmurro"]


async def test_should_search_by_partial_author(repository):
    books = await SearchBooksUseCase(repository).execute(query="oda")

    assert [b.title for b in books] == ["One Piece"]


async def test_should_filter_by_genre(repository):
    books = await SearchBooksUseCase(repository).execute(genre="mangá")

    assert [b.title for b in books] == ["One Piece"]


async def test_should_return_empty_list_when_nothing_matches(repository):
    assert await SearchBooksUseCase(repository).execute(query="naruto") == []
