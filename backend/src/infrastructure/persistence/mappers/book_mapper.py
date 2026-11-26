from src.domain.entities import Book
from src.infrastructure.persistence.models import (
    AuthorModelSQLAlchemy,
    BookModelSQLAlchemy,
)


class BookMapper:
    @staticmethod
    def to_sqlalchemy(domain: Book) -> BookModelSQLAlchemy | None:
        """Converte o modelo de Domínio (Dataclass) para o modelo do SQLAlchemy."""
        if not domain:
            return None

        domain_authors = (
            [domain.authors] if isinstance(domain.authors, str) else domain.authors
        )
        authors = (
            [AuthorModelSQLAlchemy(name=name) for name in domain_authors]
            if domain_authors
            else []
        )

        return BookModelSQLAlchemy(
            id=domain.id,
            isbn=domain.isbn,
            title=domain.title,
            authors=authors,
            publisher=domain.publisher,
            genre=list(domain.genre or []),
            theme=list(domain.theme or []),
        )

    @staticmethod
    def to_domain(db_model: BookModelSQLAlchemy) -> Book | None:
        """Converte o modelo do SQLAlchemy para a Entidade de Domínio (Dataclass)."""
        if not db_model:
            return None

        authors = (
            [author.name for author in db_model.authors] if db_model.authors else []
        )

        return Book(
            id=db_model.id,
            isbn=db_model.isbn,
            title=db_model.title,
            authors=authors,
            publisher=db_model.publisher,
            genre=list(db_model.genre or []),
            theme=list(db_model.theme or []),
        )
