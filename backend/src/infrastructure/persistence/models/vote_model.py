from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.book_model import Base


class VoteModelSQLAlchemy(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "target_entity",
            "target_id",
            name="uq_votes_user_target",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    target_entity: Mapped[str] = mapped_column(String(50), nullable=False)

    target_id: Mapped[int] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
