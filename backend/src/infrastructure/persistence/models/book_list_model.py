from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base


class BookListModelSQLAlchemy(Base):
    __tablename__ = "book_lists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    book_links: Mapped[list["BookListBookModelSQLAlchemy"]] = relationship(
        back_populates="book_list",
        cascade="all, delete-orphan",
        order_by="BookListBookModelSQLAlchemy.position",
    )


class BookListBookModelSQLAlchemy(Base):
    __tablename__ = "book_list_books"

    book_list_id: Mapped[int] = mapped_column(
        ForeignKey("book_lists.id", ondelete="CASCADE"), primary_key=True
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    book_list: Mapped[BookListModelSQLAlchemy] = relationship(
        back_populates="book_links"
    )
