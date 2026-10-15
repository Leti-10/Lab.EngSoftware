from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.domain.entities import Vote
from src.domain.entities import BookList
from src.domain.enums.enums import VoteTarget
from src.infrastructure.persistence.models.base import Base
from src.infrastructure.persistence.models.book_model import BookModelSQLAlchemy
from src.infrastructure.persistence.models.review_model import ReviewModelSQLAlchemy
from src.infrastructure.persistence.models.user_model import UserModelSQLAlchemy
from src.infrastructure.persistence.repositories import (
    InMemoryBookListRepository,
    SQLAlchemyVoteRepository,
)


@pytest.mark.asyncio
async def test_vote_repository_saves_loads_and_filters_votes():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as session:
            user = UserModelSQLAlchemy(
                username="vote-user",
                email="vote-user@example.com",
                password="hashed-password",
                role="user",
                created_at=datetime(2025, 1, 1, tzinfo=UTC),
            )
            session.add(user)
            book = BookModelSQLAlchemy(
                isbn="1234567890",
                title="A Test Book",
                publisher="Test Publisher",
            )
            session.add(book)
            await session.commit()

            review = ReviewModelSQLAlchemy(
                rating=5,
                comment="Excellent reading",
                user_id=user.id,
                book_id=book.id,
            )
            session.add(review)
            await session.commit()

            book_lists = InMemoryBookListRepository()
            book_list = book_lists.save(
                BookList(owner=user.id, name="Favorite List", description="Test list")
            )
            repository = SQLAlchemyVoteRepository(session, book_lists)
            book_vote = await repository.save(
                Vote(
                    status="like",
                    target_entity=VoteTarget.BOOK,
                    target_id=book.id,
                    user_id=user.id,
                )
            )
            review_vote = await repository.save(
                Vote(
                    status="like",
                    target_entity=VoteTarget.REVIEW,
                    target_id=review.id,
                    user_id=user.id,
                )
            )
            list_vote = await repository.save(
                Vote(
                    status="like",
                    target_entity=VoteTarget.LIST,
                    target_id=book_list.id,
                    user_id=user.id,
                )
            )

            assert await repository.get_by_id(book_vote.id) == book_vote
            assert await repository.get_by_id(999) is None
            assert await repository.find_by_filter(
                status="like",
                user_name="vote",
                target_type=VoteTarget.BOOK,
                target_name="test book",
            ) == [book_vote]
            assert await repository.find_by_filter(
                user_name="vote",
                target_type=VoteTarget.REVIEW,
                target_name="excellent",
            ) == [review_vote]
            assert await repository.find_by_filter(
                target_type=VoteTarget.LIST,
                target_name="Favorite List",
            ) == [list_vote]
            assert await repository.delete(list_vote.id)
            assert not await repository.delete(list_vote.id)
    finally:
        await engine.dispose()
