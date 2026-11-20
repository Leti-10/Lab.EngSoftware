from src.domain.entities import Review
from src.domain.exceptions import ReviewNotFoundError
from src.domain.repositories import ReviewRepository


class GetReviewByIdUseCase:
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository

    async def execute(self, review_id: int) -> Review:
        review = await self.review_repository.get_by_id(review_id)
        if review is None:
            raise ReviewNotFoundError(review_id)
        return review
