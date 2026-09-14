import pytest


@pytest.fixture
def book_repository():
    from src.infrastructure.persistence.repositories.inmemory_book_repository import (
        InMemoryBookRepository,
    )

    return InMemoryBookRepository()


@pytest.fixture
def create_book_use_case(book_repository):
    from src.application.use_cases.create_book import CreateBookUseCase

    return CreateBookUseCase(book_repository)


def test_should_create_book_successfully(create_book_use_case):
    book_data = {
        "isbn": "9788522031429",
        "genre": ["Ficção", "Romance"],
        "theme": ["Amor", "Aventura"],
        "title": "O Pequeno Príncipe",
        "author": ["Antoine de Saint-Exupéry"],
        "publisher": "Editora Agir",
    }

    result = create_book_use_case.execute(book_data)

    assert result.isbn == book_data["isbn"]
    assert result.genre == book_data["genre"]
    assert result.theme == book_data["theme"]
    assert result.title == book_data["title"]
    assert result.author == book_data["author"]
    assert result.publisher == book_data["publisher"]