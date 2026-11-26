from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.domain.enums.enums import EnumReviewSort
from src.infrastructure.persistence.models import (
    ReviewModelSQLAlchemy,
    UserModelSQLAlchemy,
    VoteModelSQLAlchemy,
)
from src.infrastructure.persistence.repositories import SQLAlchemyReviewRepository


async def test_review_page_sorts_by_recent_or_like_count(postgres_engine: AsyncEngine):
    session_factory = async_sessionmaker(postgres_engine, expire_on_commit=False)

    async with session_factory() as session:
        users = [
            UserModelSQLAlchemy(
                username=f"reader-{index}",
                email=f"reader-{index}@example.com",
                password="hashed-password",
            )
            for index in range(4)
        ]
        session.add_all(users)
        await session.flush()

        oldest = ReviewModelSQLAlchemy(
            rating=5,
            comment="Most liked",
            user_id=users[0].id,
            book_id=1,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        newest = ReviewModelSQLAlchemy(
            rating=4,
            comment="Newest",
            user_id=users[0].id,
            book_id=2,
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        middle = ReviewModelSQLAlchemy(
            rating=3,
            comment="Second most liked",
            user_id=users[0].id,
            book_id=3,
            created_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        session.add_all([oldest, newest, middle])
        await session.flush()
        session.add_all(
            [
                VoteModelSQLAlchemy(
                    status="like",
                    target_entity="reviews",
                    target_id=oldest.id,
                    user_id=users[1].id,
                ),
                VoteModelSQLAlchemy(
                    status="like",
                    target_entity="reviews",
                    target_id=oldest.id,
                    user_id=users[2].id,
                ),
                VoteModelSQLAlchemy(
                    status="like",
                    target_entity="reviews",
                    target_id=middle.id,
                    user_id=users[3].id,
                ),
            ]
        )
        await session.commit()

        repository = SQLAlchemyReviewRepository(session)
        recent, recent_total = await repository.get_page(
            1, 2, EnumReviewSort.RECENT
        )
        popular, popular_total = await repository.get_page(
            1, 2, EnumReviewSort.POPULAR
        )
        last_page, _ = await repository.get_page(2, 2, EnumReviewSort.RECENT)

    assert [review.id for review in recent] == [newest.id, middle.id]
    assert [review.id for review in popular] == [oldest.id, middle.id]
    assert [review.id for review in last_page] == [oldest.id]
    assert recent_total == popular_total == 3
