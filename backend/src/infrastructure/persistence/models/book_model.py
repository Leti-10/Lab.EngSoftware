from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy import Integer, String


class Base(DeclarativeBase):
    pass


class BookModelSQLAlchemy(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(15), nullable=False)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    publisher: Mapped[str] = mapped_column(String(60), nullable=True)
