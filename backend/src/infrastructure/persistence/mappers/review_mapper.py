from src.domain.entities import Review
from src.infrastructure.persistence.models import ReviewModelSQLAlchemy


class ReviewMapper:
    @staticmethod
    def to_sqlalchemy(domain: Review) -> ReviewModelSQLAlchemy | None:
        if domain is None:
            return None

        return ReviewModelSQLAlchemy(
            id=domain.id,
            rating=domain.rating,
            comment=domain.comment,
            user_id=domain.user_id,
            book_id=domain.book_id,
        )

    @staticmethod
    def to_domain(db_model: ReviewModelSQLAlchemy) -> Review | None:
        if db_model is None:
            return None

        return Review(
            id=db_model.id,
            rating=db_model.rating,
            comment=db_model.comment,
            user_id=db_model.user_id,
            book_id=db_model.book_id,
        )