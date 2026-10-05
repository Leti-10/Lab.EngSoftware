from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base
from src.infrastructure.persistence.models.user_model import UserModelSQLAlchemy

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.book_model import BookModelSQLAlchemy


class ReviewModelSQLAlchemy(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped[UserModelSQLAlchemy] = relationship(back_populates="reviews")
    book: Mapped["BookModelSQLAlchemy"] = relationship(back_populates="reviews")
