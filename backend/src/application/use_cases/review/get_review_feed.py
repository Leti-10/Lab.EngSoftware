from src.domain.entities import Review
from src.domain.enums.enums import EnumReviewSort
from src.domain.repositories import ReviewRepository


class GetReviewFeedUseCase:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def execute(
        self, page: int, page_size: int, sort_by: EnumReviewSort
    ) -> tuple[list[Review], int]:
        return await self.repository.get_page(page, page_size, sort_by)
