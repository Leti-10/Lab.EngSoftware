from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ListReviewORM(Base):
    __tablename__ = "list_review"

    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id"),
        primary_key=True
    )

    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id"),
        primary_key=True
    )