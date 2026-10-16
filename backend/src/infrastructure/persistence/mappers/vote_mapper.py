from src.domain.entities import Vote
from src.infrastructure.persistence.models import VoteModelSQLAlchemy


class VoteMapper:
    @staticmethod
    def to_sqlalchemy(domain: Vote) -> VoteModelSQLAlchemy | None:
        if domain is None:
            return None

        return VoteModelSQLAlchemy(
            id=domain.id,
            status=domain.status,
            target_entity=getattr(domain.target_entity, "value", domain.target_entity),
            target_id=domain.target_id,
            user_id=domain.user_id,
        )

    @staticmethod
    def to_domain(db_model: VoteModelSQLAlchemy) -> Vote | None:
        if db_model is None:
            return None

        return Vote(
            id=db_model.id,
            status=db_model.status,
            target_entity=db_model.target_entity,
            target_id=db_model.target_id,
            user_id=db_model.user_id,
        )