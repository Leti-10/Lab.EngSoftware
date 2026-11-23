from src.domain.entities import Review
from src.domain.exceptions import InvalidReviewError
from src.domain.repositories import ReviewRepository


class CreateReviewUseCase:
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository

    async def execute(self, new_review: Review) -> Review:
        if new_review is None:
            raise InvalidReviewError()

        return await self.review_repository.save(new_review)
