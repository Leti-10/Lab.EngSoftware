from src.domain.entities import Review
from src.domain.repositories import ReviewRepository


class FilterReviewsUseCase:
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository

    async def execute(
        self,
        rating: int | None = None,
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
    ) -> list[Review]:
        return await self.review_repository.find_by_filter(
            rating=rating,
            username=username,
            book_title=book_title,
            comment=comment,
        )
