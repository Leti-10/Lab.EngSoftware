from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Review
from src.domain.repositories import ReviewRepository
from src.infrastructure.persistence.mappers import ReviewMapper
from src.infrastructure.persistence.models import ReviewModelSQLAlchemy


class SQLAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, review: Review) -> Review:
        model = ReviewMapper.to_sqlalchemy(review)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return ReviewMapper.to_domain(model)

    async def get_by_id(self, review_id: int) -> Review | None:
        result = await self.session.execute(
            select(ReviewModelSQLAlchemy).where(ReviewModelSQLAlchemy.id == review_id)
        )
        model = result.scalar_one_or_none()
        return ReviewMapper.to_domain(model)

    async def find_by_filter(
        self,
        rating: int | None = None,
        user_id: int | None = None,
        book_id: int | None = None,
        comment: str | None = None,
    ) -> list[Review]:
        query = select(ReviewModelSQLAlchemy)
        if rating is not None:
            query = query.where(ReviewModelSQLAlchemy.rating == rating)
        if user_id is not None:
            query = query.where(ReviewModelSQLAlchemy.user_id == user_id)
        if book_id is not None:
            query = query.where(ReviewModelSQLAlchemy.book_id == book_id)
        if comment:
            query = query.where(ReviewModelSQLAlchemy.comment.ilike(f"%{comment}%"))

        result = await self.session.execute(query)
        return [ReviewMapper.to_domain(model) for model in result.scalars().all()]