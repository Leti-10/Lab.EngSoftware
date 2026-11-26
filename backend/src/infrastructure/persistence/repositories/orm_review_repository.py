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
from src.infrastructure.telemetry import logger_decorator


class SQLAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @logger_decorator
    async def save(self, review: Review) -> Review:
        try:
            model = ReviewMapper.to_sqlalchemy(review)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            if model is None:
                raise ValueError(
                    "Failed to save the review. The model is None."
                )
            return ReviewMapper.to_domain(model)
        except IntegrityError:
            await self.session.rollback()
            raise

    @logger_decorator
    async def update(self, review: Review) -> Review | None:
        if review.id is None:
            return None

        model = await self.session.get(ReviewModelSQLAlchemy, review.id)
        if model is None:
            return None

        model.rating = review.rating
        model.comment = review.comment
        model.isSpoiler = review.isSpoiler
        model.user_id = review.user_id
        model.book_id = review.book_id

        try:
            await self.session.commit()
            await self.session.refresh(model)
        except IntegrityError:
            await self.session.rollback()
            raise

        return ReviewMapper.to_domain(model)

    @logger_decorator
    async def get_by_id(self, review_id: int) -> Review | None:
        result = await self.session.execute(
            select(ReviewModelSQLAlchemy).where(ReviewModelSQLAlchemy.id == review_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return ReviewMapper.to_domain(model)

    @logger_decorator
    async def get_all(self, order_by: str = "id") -> list[Review]:
        query = select(ReviewModelSQLAlchemy)
        if order_by == "rating":
            query = query.order_by(ReviewModelSQLAlchemy.rating.desc())
        elif order_by == "created_at":
            query = query.order_by(ReviewModelSQLAlchemy.created_at.desc())
        else:
            query = query.order_by(ReviewModelSQLAlchemy.id)

        result = await self.session.execute(query)
        return [
            domain
            for model in result.scalars().all()
            if (domain := ReviewMapper.to_domain(model)) is not None
        ]

    @logger_decorator
    async def find_by_filter(
        self,
        rating: int | None = None,
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
        book_id: int | None = None,
        user_id: int | None = None,
    ) -> list[Review | None]:
        query = select(ReviewModelSQLAlchemy).order_by(ReviewModelSQLAlchemy.id.desc())
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
                ReviewModelSQLAlchemy.book_id.in_(
                    select(BookModelSQLAlchemy.id).where(
                        BookModelSQLAlchemy.title.ilike(f"%{book_title}%")
                    )
                )
            )
        if book_id is not None:
            query = query.where(ReviewModelSQLAlchemy.book_id == book_id)
        if user_id is not None:
            query = query.where(ReviewModelSQLAlchemy.user_id == user_id)
        if comment:
            query = query.where(ReviewModelSQLAlchemy.comment.ilike(f"%{comment}%"))

        result = await self.session.execute(query)
        return [ReviewMapper.to_domain(model) for model in result.scalars().all()]
