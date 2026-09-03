from sqlalchemy.orm import mapped_column, Mapped, registry
from sqlalchemy import ForeignKey, Enum as SQLEnum
from enum import Enum

class StatusEnum(str, Enum):
    UPVOTE = "Upvote"
    DOWNVOTE = "DownVote"
    READED = "Readed" # Apenas para Book
    READING = "Reading" # Apenas para Book
    WANT_TO_READ = "Want to read" # Apenas para Book

class TargetEnum(str, Enum): # Tipo da Entidade
    BOOK = "books"
    REVIEW = "reviews"
    LIST = "lists"

table_registry = registry()

@table_registry.mapped_as_dataclass
class Vote:
    __table_name__ = "votes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum), nullable=False)
    target_entity: Mapped[TargetEnum] = mapped_column(SQLEnum(TargetEnum), nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))