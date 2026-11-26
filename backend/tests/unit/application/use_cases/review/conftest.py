import pytest

from src.infrastructure.persistence.repositories import InMemoryReviewRepository


@pytest.fixture
def review_repository() -> InMemoryReviewRepository:
    return InMemoryReviewRepository()
