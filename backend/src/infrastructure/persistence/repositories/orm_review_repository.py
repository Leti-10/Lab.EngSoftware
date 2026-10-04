from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.domain.entities import Review
from src.domain.repositories import ReviewRepository
from src.infrastructure.persistence.mappers import ReviewMapper
from src.infrastructure.persistence.models import (
    BookModelSQLAlchemy,
    ReviewModelSQLAlchemy,
    UserModelSQLAlchemy,
)


class SQLAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, review: Review) -> Review:
        model = ReviewMapper.to_sqlalchemy(review)
        self.session.add(model)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
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
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
    ) -> list[Review]:
        query = select(ReviewModelSQLAlchemy)
        if rating is not None:
            query = query.where(ReviewModelSQLAlchemy.rating == rating)
        if username:
            query = query.where(
                ReviewModelSQLAlchemy.user.has(
                    UserModelSQLAlchemy.username.ilike(f"%{username}%")
                )
            )
        if book_title:
            query = query.where(
                ReviewModelSQLAlchemy.book.has(
                    BookModelSQLAlchemy.title.ilike(f"%{book_title}%")
                )
            )
        if comment:
            query = query.where(ReviewModelSQLAlchemy.comment.ilike(f"%{comment}%"))

        result = await self.session.execute(query)
        return [ReviewMapper.to_domain(model) for model in result.scalars().all()]
