import pytest

from src.infrastructure.persistence.repositories import InMemoryBookRepository


@pytest.fixture
def book_repository() -> InMemoryBookRepository:
    return InMemoryBookRepository()
