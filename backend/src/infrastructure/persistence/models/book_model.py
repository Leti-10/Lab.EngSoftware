from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Column, ForeignKey, Table

from src.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.review_model import ReviewModelSQLAlchemy


book_author_association = Table(
    "book_author",
    Base.metadata,
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)


class AuthorModelSQLAlchemy(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    books: Mapped[list["BookModelSQLAlchemy"]] = relationship(
        secondary=book_author_association, back_populates="authors"
    )


class BookModelSQLAlchemy(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    publisher: Mapped[str] = mapped_column(nullable=True)
    authors: Mapped[list["AuthorModelSQLAlchemy"]] = relationship(
        secondary=book_author_association, back_populates="books"
    )
    reviews: Mapped[list["ReviewModelSQLAlchemy"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
