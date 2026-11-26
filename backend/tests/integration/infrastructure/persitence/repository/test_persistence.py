from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.models import (
    AuthorModelSQLAlchemy,
    BookModelSQLAlchemy,
    CommentModelSQLAlchemy,
    FollowModelSQLAlchemy,
    NotificationModelSQLAlchemy,
    NotificationPreferenceModelSQLAlchemy,
    ReadingModelSQLAlchemy,
    ReportModelSQLAlchemy,
    ReviewModelSQLAlchemy,
    UserModelSQLAlchemy,
    VoteModelSQLAlchemy,
)


async def test_persists_all_business_entities(postgres_engine: AsyncEngine):
    session_factory = async_sessionmaker(postgres_engine, expire_on_commit=False)

    async with session_factory() as session:
        user = UserModelSQLAlchemy(
            username="persistence_user",
            email="persistence@example.com",
            password="hashed-password",
            role="user",
            bio="Leitor",
            avatar_url="https://example.com/avatar.png",
            cover_url="https://example.com/cover.png",
        )
        actor = UserModelSQLAlchemy(
            username="persistence_actor",
            email="actor@example.com",
            password="hashed-password",
        )
        author = AuthorModelSQLAlchemy(name="Autor")
        book = BookModelSQLAlchemy(
            isbn="9780000000001",
            title="Livro persistido",
            publisher="Editora",
            genre=["Ficção"],
            theme=["Aventura"],
            authors=[author],
        )
        session.add_all([user, actor, book])
        await session.flush()

        review = ReviewModelSQLAlchemy(
            rating=5,
            comment="Excelente",
            isSpoiler=False,
            user_id=user.id,
            book_id=book.id,
            created_at=datetime.now(timezone.utc),
        )
        session.add(review)
        await session.flush()

        reading = ReadingModelSQLAlchemy(
            status="reading",
            book_id=book.id,
            user_id=user.id,
        )
        report = ReportModelSQLAlchemy(
            user_id=user.id,
            target_id=review.id,
            target_entity="reviews",
            description="Denúncia persistida",
        )
        comment = CommentModelSQLAlchemy(
            text="Comentário persistido",
            review_id=review.id,
            user_id=actor.id,
            created_at=datetime.now(timezone.utc),
        )
        follow = FollowModelSQLAlchemy(
            follower_id=user.id,
            target_type="users",
            target_id=actor.id,
            created_at=datetime.now(timezone.utc),
        )
        notification = NotificationModelSQLAlchemy(
            user_id=user.id,
            type="comment",
            actor_id=actor.id,
            review_id=review.id,
            book_id=book.id,
            read=False,
            created_at=datetime.now(timezone.utc),
        )
        preference = NotificationPreferenceModelSQLAlchemy(
            user_id=user.id,
            likes=False,
            comments=True,
            follows=False,
        )
        vote = VoteModelSQLAlchemy(
            status="like",
            target_entity="reviews",
            target_id=review.id,
            user_id=user.id,
        )
        session.add_all(
            [reading, report, comment, follow, notification, preference, vote]
        )
        await session.commit()

        user_id = user.id
        actor_id = actor.id
        book_id = book.id
        author_id = author.id
        review_id = review.id

    async with session_factory() as session:
        persisted_user = await session.scalar(
            select(UserModelSQLAlchemy).where(UserModelSQLAlchemy.id == user_id)
        )
        persisted_book = await session.scalar(
            select(BookModelSQLAlchemy)
            .options(selectinload(BookModelSQLAlchemy.authors))
            .where(BookModelSQLAlchemy.id == book_id)
        )
        persisted_author = await session.scalar(
            select(AuthorModelSQLAlchemy).where(AuthorModelSQLAlchemy.id == author_id)
        )
        persisted_review = await session.scalar(
            select(ReviewModelSQLAlchemy).where(ReviewModelSQLAlchemy.id == review_id)
        )
        persisted_reading = await session.scalar(
            select(ReadingModelSQLAlchemy).where(
                ReadingModelSQLAlchemy.user_id == user_id,
                ReadingModelSQLAlchemy.book_id == book_id,
            )
        )
        persisted_report = await session.scalar(
            select(ReportModelSQLAlchemy).where(
                ReportModelSQLAlchemy.user_id == user_id
            )
        )
        persisted_comment = await session.scalar(
            select(CommentModelSQLAlchemy).where(
                CommentModelSQLAlchemy.review_id == review_id
            )
        )
        persisted_follow = await session.scalar(
            select(FollowModelSQLAlchemy).where(
                FollowModelSQLAlchemy.follower_id == user_id
            )
        )
        persisted_notification = await session.scalar(
            select(NotificationModelSQLAlchemy).where(
                NotificationModelSQLAlchemy.user_id == user_id
            )
        )
        persisted_preference = await session.get(
            NotificationPreferenceModelSQLAlchemy, user_id
        )
        persisted_vote = await session.scalar(
            select(VoteModelSQLAlchemy).where(VoteModelSQLAlchemy.user_id == user_id)
        )

        assert persisted_user is not None
        assert persisted_user.username == "persistence_user"
        assert persisted_user.bio == "Leitor"
        assert persisted_book is not None
        assert persisted_book.title == "Livro persistido"
        assert persisted_book.genre == ["Ficção"]
        assert [author.name for author in persisted_book.authors] == ["Autor"]
        assert persisted_author is not None
        assert persisted_author.id == author_id
        assert persisted_review is not None
        assert persisted_review.rating == 5
        assert persisted_review.user_id == user_id
        assert persisted_reading is not None
        assert persisted_reading.status == "reading"
        assert persisted_report is not None
        assert persisted_report.description == "Denúncia persistida"
        assert persisted_comment is not None
        assert persisted_comment.text == "Comentário persistido"
        assert persisted_comment.user_id == actor_id
        assert persisted_follow is not None
        assert persisted_follow.target_id == actor_id
        assert persisted_notification is not None
        assert persisted_notification.type == "comment"
        assert persisted_preference is not None
        assert persisted_preference.likes is False
        assert persisted_vote is not None
        assert persisted_vote.target_id == review_id
