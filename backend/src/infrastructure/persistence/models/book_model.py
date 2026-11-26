from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import ARRAY

from src.infrastructure.persistence.models.base import Base

book_author_association = Table(
    "book_author",
    Base.metadata,
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)


class AuthorModelSQLAlchemy(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True, default="unknown")

    books: Mapped[list["BookModelSQLAlchemy"]] = relationship(
        secondary=book_author_association, back_populates="authors"
    )


class BookModelSQLAlchemy(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    publisher: Mapped[str] = mapped_column(nullable=True)
    genre: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    theme: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    authors: Mapped[list["AuthorModelSQLAlchemy"]] = relationship(
        secondary=book_author_association, back_populates="books"
    )
