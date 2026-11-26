from datetime import datetime, timezone
from logging import getLogger

import pytest

from src.application.use_cases.review import CreateReviewUseCase
from src.domain.entities import Book, Review

logger = getLogger(__name__)


@pytest.fixture
def mock_review_repository(mocker):
    return mocker.Mock()


@pytest.mark.asyncio
async def test_create_review(review_repository):
    book = Book(
        id=1,
        isbn="12345678900",
        title="Test Book",
        authors="Test Author",
        publisher="Test Publisher",
    )
    review = Review(
        id=1,
        rating=5,
        user_id=1,
        book_id=book.id or 1,
        comment="Great book!",
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
    )
    use_case = CreateReviewUseCase(review_repository)
    created_review = await use_case.execute(review)

    assert created_review is not None
    assert created_review.id == 1
    assert created_review.rating == 5
    assert created_review.user_id == 1
    assert created_review.book_id == book.id
    assert created_review.comment == "Great book!"
    assert created_review.created_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
