from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base


class ReportModelSQLAlchemy(Base):
    __tablename__ = "reports"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "target_entity",
            "target_id",
            name="uq_reports_user_target",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    target_entity: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
