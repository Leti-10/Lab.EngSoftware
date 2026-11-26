from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.domain.entities import BookList
from src.infrastructure.persistence.models import (
    Base,
    BookModelSQLAlchemy,
    UserModelSQLAlchemy,
)
from src.infrastructure.persistence.repositories import SQLAlchemyBookListRepository


async def test_book_list_repository_persists_lists_and_ordered_books(
    postgres_engine: AsyncEngine,
):
    async with postgres_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(postgres_engine, expire_on_commit=False)
    async with session_factory() as session:
        user = UserModelSQLAlchemy(
            username="list-owner",
            email="list-owner@example.com",
            password="hashed-password",
        )
        books = [
            BookModelSQLAlchemy(
                isbn=f"978000000000{index}",
                title=f"Book {index}",
                publisher="Test Publisher",
                genre=[],
                theme=[],
            )
            for index in range(1, 3)
        ]
        session.add_all([user, *books])
        await session.commit()

        repository = SQLAlchemyBookListRepository(session)
        created = await repository.save(
            BookList(owner=user.id, name="Persistent list", description="Test list")
        )
        created.books = [books[1].id, books[0].id]
        updated = await repository.update(created)

        assert updated is not None
        assert updated.books == [books[1].id, books[0].id]

        list_id = created.id
        owner_id = user.id

    async with session_factory() as session:
        repository = SQLAlchemyBookListRepository(session)
        persisted = await repository.get_by_id(list_id)

        assert persisted is not None
        assert persisted.owner == owner_id
        assert persisted.books == [books[1].id, books[0].id]
        assert (await repository.get_by_name("persistent list")) == persisted
        assert await repository.list_by_owner(owner_id) == [persisted]
        assert await repository.delete(list_id)
        assert await repository.get_by_id(list_id) is None
