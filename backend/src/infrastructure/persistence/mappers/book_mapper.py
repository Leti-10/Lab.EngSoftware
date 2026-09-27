from src.domain.entities import Book
from src.infrastructure.persistence.models.book_model import BookModelSQLAlchemy


class BookMapper:
    @staticmethod
    def to_sqlalchemy(domain: Book) -> BookModelSQLAlchemy:
        """Converte o modelo de Domínio (Dataclass) para o modelo do SQLAlchemy."""
        if not domain:
            return None
        return BookModelSQLAlchemy(
            isbn=domain.isbn, title=domain.title, publisher=domain.publisher
        )

    @staticmethod
    def to_domain(db_model: BookModelSQLAlchemy) -> Book:
        """Converte o modelo do SQLAlchemy para a Entidade de Domínio (Dataclass)."""
        if not db_model:
            return None
        return Book(
            isbn=db_model.isbn, title=db_model.title, publisher=db_model.publisher
        )
