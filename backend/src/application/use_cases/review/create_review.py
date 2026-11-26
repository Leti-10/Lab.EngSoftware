from logging import getLogger

from src.domain.entities import Review
from src.domain.exceptions import InvalidReviewError
from src.domain.repositories import ReviewRepository

logger = getLogger(__name__)


class CreateReviewUseCase:
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository

    async def execute(self, new_review: Review) -> Review:
        if new_review is None:
            raise InvalidReviewError()

        created_review = await self.review_repository.save(new_review)
        logger.info(
            "Review created successfully:",
            extra={
                "review_id": created_review.id,
                "rating": created_review.rating,
                "user_id": created_review.user_id,
                "book_id": created_review.book_id,
                "comment": created_review.comment,
                "created_at": created_review.created_at,
            },
        )
        return created_review
