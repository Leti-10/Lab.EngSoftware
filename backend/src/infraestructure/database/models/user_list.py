from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserListORM(Base):
    __tablename__ = "user_list"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )

    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id"),
        primary_key=True
    )