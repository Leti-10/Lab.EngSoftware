from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities import BookList
from src.domain.repositories import BookListRepository
from src.infrastructure.persistence.models.book_list_model import (
    BookListBookModelSQLAlchemy,
    BookListModelSQLAlchemy,
)
from src.infrastructure.telemetry import logger_decorator


class SQLAlchemyBookListRepository(BookListRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(model: BookListModelSQLAlchemy) -> BookList:
        book_list = BookList(
            owner=model.owner_id,
            name=model.name,
            description=model.description,
            private=model.private,
            books=[link.book_id for link in model.book_links],
        )
        book_list.id = model.id
        return book_list

    @staticmethod
    def _book_links(book_ids: list[int]) -> list[BookListBookModelSQLAlchemy]:
        return [
            BookListBookModelSQLAlchemy(book_id=book_id, position=position)
            for position, book_id in enumerate(book_ids)
        ]

    @staticmethod
    def _replace_book_links(
        model: BookListModelSQLAlchemy, book_ids: list[int]
    ) -> None:
        existing = {link.book_id: link for link in model.book_links}
        links = []
        for position, book_id in enumerate(book_ids):
            link = existing.get(book_id)
            if link is None:
                link = BookListBookModelSQLAlchemy(book_id=book_id, position=position)
            else:
                link.position = position
            links.append(link)
        model.book_links = links

    @logger_decorator
    async def save(self, book_list: BookList) -> BookList:
        model = BookListModelSQLAlchemy(
            owner_id=book_list.owner,
            name=book_list.name,
            description=book_list.description,
            private=book_list.private,
            book_links=self._book_links(book_list.books),
        )
        self.session.add(model)
        await self.session.flush()
        saved = self._to_domain(model)
        await self.session.commit()
        return saved

    @logger_decorator
    async def update(self, book_list: BookList) -> BookList | None:
        model = await self.session.get(
            BookListModelSQLAlchemy,
            book_list.id,
            options=[selectinload(BookListModelSQLAlchemy.book_links)],
        )
        if model is None:
            return None

        model.owner_id = book_list.owner
        model.name = book_list.name
        model.description = book_list.description
        model.private = book_list.private
        self._replace_book_links(model, book_list.books)
        await self.session.flush()
        updated = self._to_domain(model)
        await self.session.commit()
        return updated

    @logger_decorator
    async def get_by_id(self, list_id: int) -> BookList | None:
        result = await self.session.execute(
            select(BookListModelSQLAlchemy)
            .options(selectinload(BookListModelSQLAlchemy.book_links))
            .where(BookListModelSQLAlchemy.id == list_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    @logger_decorator
    async def get_by_name(self, name: str) -> BookList | None:
        result = await self.session.execute(
            select(BookListModelSQLAlchemy)
            .options(selectinload(BookListModelSQLAlchemy.book_links))
            .where(func.lower(BookListModelSQLAlchemy.name) == name.lower())
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    @logger_decorator
    async def delete(self, list_id: int) -> bool:
        model = await self.session.get(BookListModelSQLAlchemy, list_id)
        if model is None:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    @logger_decorator
    async def list_by_owner(self, owner_id: int) -> list[BookList]:
        result = await self.session.execute(
            select(BookListModelSQLAlchemy)
            .options(selectinload(BookListModelSQLAlchemy.book_links))
            .where(BookListModelSQLAlchemy.owner_id == owner_id)
            .order_by(BookListModelSQLAlchemy.id)
        )
        return [self._to_domain(model) for model in result.scalars().all()]
