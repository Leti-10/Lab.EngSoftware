import pytest

from src.application.use_cases.review import CreateReviewUseCase
from src.domain.exceptions import InvalidReviewError


@pytest.mark.asyncio
async def test_create_review_rejects_none_with_domain_exception():
    with pytest.raises(InvalidReviewError):
        await CreateReviewUseCase(None).execute(None)
