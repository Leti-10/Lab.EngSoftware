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

    async def save(self, review: Review) -> Review | None:
        try:
            model = ReviewMapper.to_sqlalchemy(review)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            if model is None:
                raise ValueError(
                    "Failed to save the review. The model is None."
                )  # TODO: Handle correctly the case when the model is None
            return ReviewMapper.to_domain(model)
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_by_id(self, review_id: int) -> Review | None:
        result = await self.session.execute(
            select(ReviewModelSQLAlchemy).where(ReviewModelSQLAlchemy.id == review_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return ReviewMapper.to_domain(model)

    async def find_by_filter(
        self,
        rating: int | None = None,
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
    ) -> list[Review | None]:
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
