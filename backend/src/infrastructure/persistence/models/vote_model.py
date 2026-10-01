from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.book_model import Base


class VoteModelSQLAlchemy(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    target_entity: Mapped[str] = mapped_column(String(50), nullable=False)

    target_id: Mapped[int] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
