from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Book
from src.infrastructure.persistence.models import BookModelSQLAlchemy
from src.domain.repositories import BookRepository
from src.infrastructure.persistence.mappers import BookMapper


class SQLAlchemyRepository(BookRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, book: Book) -> Book:
        _book_model = BookMapper.to_sqlalchemy(book)
        self.session.add(_book_model)

        await self.session.commit()
        await self.session.refresh(_book_model)

        domain_book = BookMapper.to_domain(_book_model)
        return domain_book

    async def update(self, book: Book) -> Book:
        model = await self.session.get(
            BookModelSQLAlchemy,
            book.id,
            options=[selectinload(BookModelSQLAlchemy.authors)],
        )
        if model is None:
            raise ValueError(f"Book with id {book.id} not found.")

        updated = BookMapper.to_sqlalchemy(book)
        model.isbn = updated.isbn
        model.title = updated.title
        model.publisher = updated.publisher
        model.authors = updated.authors

        await self.session.commit()
        await self.session.refresh(model, attribute_names=["authors"])
        return BookMapper.to_domain(model)

    async def delete(self, book_id: int) -> bool:
        model = await self.session.get(BookModelSQLAlchemy, book_id)
        if model is None:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True

    async def get_by_id(self, book_id: int) -> Book | None:
        query = (
            select(BookModelSQLAlchemy)
            .where(BookModelSQLAlchemy.id == book_id)
            .options(selectinload(BookModelSQLAlchemy.authors))
        )
        result = await self.session.execute(query)

        book_alchemy = result.scalar_one_or_none()

        if book_alchemy is None:
            return None

        return BookMapper.to_domain(book_alchemy)

    async def get_by_isbn(self, isbn: str) -> Book | None:
        return await super().get_by_isbn(isbn)

    async def find_by_filter(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        theme: str | None = None,
        publisher: str | None = None,
    ) -> list[Book | None]:
        return await super().find_by_filter(title, author, genre, theme, publisher)
