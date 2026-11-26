from src.domain.entities import Review
from src.infrastructure.persistence.models import ReviewModelSQLAlchemy


class ReviewMapper:
    @staticmethod
    def to_sqlalchemy(domain: Review) -> ReviewModelSQLAlchemy:
        if domain is None:
            return None

        return ReviewModelSQLAlchemy(
            id=domain.id,
            rating=domain.rating,
            comment=domain.comment,
            isSpoiler=domain.isSpoiler,
            user_id=domain.user_id,
            book_id=domain.book_id,
            created_at=domain.created_at,
        )

    @staticmethod
    def to_domain(db_model: ReviewModelSQLAlchemy) -> Review:
        if db_model is None:
            return None

        return Review(
            id=db_model.id,
            rating=db_model.rating,
            comment=db_model.comment,
            isSpoiler=db_model.isSpoiler,
            user_id=db_model.user_id,
            book_id=db_model.book_id,
            created_at=db_model.created_at,
        )
