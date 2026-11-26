from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities import Book
from src.domain.repositories import BookRepository
from src.infrastructure.persistence.mappers import BookMapper
from src.infrastructure.persistence.models import (
    AuthorModelSQLAlchemy,
    BookModelSQLAlchemy,
)
from src.infrastructure.telemetry import logger_decorator
from src.infrastructure.telemetry.performance_decorator import perf_decorator


class SQLAlchemyRepository(BookRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @logger_decorator
    @perf_decorator
    async def save(self, book: Book) -> Book:
        book_model = BookMapper.to_sqlalchemy(book)
        if book_model is None:
            raise ValueError("O livro não pode ser nulo.")

        self.session.add(book_model)
        try:
            await self.session.commit()
            await self.session.refresh(book_model, attribute_names=["authors"])
        except IntegrityError:
            await self.session.rollback()
            raise

        saved = BookMapper.to_domain(book_model)
        if saved is None:
            raise ValueError("O livro salvo não pôde ser convertido.")
        return saved

    @logger_decorator
    @perf_decorator
    async def update(self, book: Book) -> Book:
        if book.id is None:
            raise ValueError("Book ID is required for update.")

        model = await self.session.get(
            BookModelSQLAlchemy,
            book.id,
            options=[selectinload(BookModelSQLAlchemy.authors)],
        )
        if model is None:
            raise ValueError(f"Book with id {book.id} not found.")

        updated = BookMapper.to_sqlalchemy(book)
        if updated is None:
            raise ValueError("O livro não pode ser nulo.")
        model.isbn = updated.isbn
        model.title = updated.title
        model.publisher = updated.publisher
        model.authors = [
            AuthorModelSQLAlchemy(name=author.name) for author in updated.authors
        ]
        model.genre = updated.genre
        model.theme = updated.theme

        try:
            await self.session.commit()
            await self.session.refresh(model, attribute_names=["authors"])
        except IntegrityError:
            await self.session.rollback()
            raise

        updated_book = BookMapper.to_domain(model)
        if updated_book is None:
            raise ValueError("O livro atualizado não pôde ser convertido.")
        return updated_book

    @logger_decorator
    @perf_decorator
    async def delete(self, book_id: int) -> bool:
        query = (
            select(BookModelSQLAlchemy)
            .where(BookModelSQLAlchemy.id == book_id)
            .options(selectinload(BookModelSQLAlchemy.authors))
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return False

        try:
            await self.session.delete(model)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        return True

    @logger_decorator
    @perf_decorator
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

    @logger_decorator
    @perf_decorator
    async def get_by_isbn(self, isbn: str) -> Book | None:
        query = (
            select(BookModelSQLAlchemy)
            .where(BookModelSQLAlchemy.isbn == isbn)
            .options(selectinload(BookModelSQLAlchemy.authors))
        )
        result = await self.session.execute(query)
        book_alchemy = result.scalar_one_or_none()
        if book_alchemy is None:
            return None
        return BookMapper.to_domain(book_alchemy)

    @logger_decorator
    @perf_decorator
    async def find_by_filter(
        self,
        isbn: str | None = None,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        theme: str | None = None,
        publisher: str | None = None,
    ) -> list[Book | None]:
        filters = []
        if isbn:
            filters.append(BookModelSQLAlchemy.isbn.ilike(f"%{isbn}%"))
        if title:
            filters.append(BookModelSQLAlchemy.title.ilike(f"%{title}%"))
        if author:
            filters.append(
                BookModelSQLAlchemy.authors.any(
                    AuthorModelSQLAlchemy.name.ilike(f"%{author}%")
                )
            )
        if genre:
            filters.append(BookModelSQLAlchemy.genre.contains([genre]))
        if theme:
            filters.append(BookModelSQLAlchemy.theme.contains([theme]))
        if publisher:
            filters.append(BookModelSQLAlchemy.publisher.ilike(f"%{publisher}%"))

        if not filters:
            return []

        stmt = (
            select(BookModelSQLAlchemy)
            .where(or_(*filters))
            .options(selectinload(BookModelSQLAlchemy.authors))
        )
        result = await self.session.execute(stmt)
        books = result.scalars().all()
        return [BookMapper.to_domain(book) for book in books]

    @logger_decorator
    @perf_decorator
    async def get_all(self) -> list[Book]:
        query = select(BookModelSQLAlchemy).options(
            selectinload(BookModelSQLAlchemy.authors)
        )
        result = await self.session.execute(query)
        books_alchemy = result.scalars().all()
        return [
            domain_book
            for book in books_alchemy
            if (domain_book := BookMapper.to_domain(book)) is not None
        ]
