from src.domain.entities import Review
from src.domain.exceptions import ReviewNotFoundError
from src.domain.repositories import ReviewRepository


class UpdateReviewUseCase:
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository

    async def execute(self, review_id: int, updated: Review) -> Review:
        if await self.review_repository.get_by_id(review_id) is None:
            raise ReviewNotFoundError(review_id)

        updated.id = review_id
        result = await self.review_repository.update(updated)
        if result is None:
            raise ReviewNotFoundError(review_id)
        return result
