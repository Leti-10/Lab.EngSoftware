from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.book_model import Base


class ReviewModelSQLAlchemy(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
