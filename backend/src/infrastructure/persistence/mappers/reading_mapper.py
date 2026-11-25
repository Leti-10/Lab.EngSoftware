from src.domain.entities import Reading
from src.infrastructure.persistence.models import ReadingModelSQLAlchemy


class ReadingMapper:
    @staticmethod
    def to_sqlalchemy(domain: Reading) -> ReadingModelSQLAlchemy:
        return ReadingModelSQLAlchemy(
            id=domain.id,
            status=domain.status.value,
            book_id=domain.book_id,
            user_id=domain.user_id,
        )

    @staticmethod
    def to_domain(db_model: ReadingModelSQLAlchemy) -> Reading:
        return Reading(
            id=db_model.id,
            status=db_model.status,
            book_id=db_model.book_id,
            user_id=db_model.user_id,
        )
