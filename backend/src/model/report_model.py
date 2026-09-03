from enum import Enum
from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, registry

class TargetEnum(Enum):
    BOOK = "books"
    LIST = "lists"
    USER = "users"
    REVIEW = "reviews"

table_registry = registry()

@table_registry.mapped_as_dataclass
class Report:
    __table_name__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    description: Mapped[str] = mapped_column(nullable=False)
    target_entity: Mapped[TargetEnum] = mapped_column(SQLEnum(TargetEnum), nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)