from src.domain.entities import Report
from src.infrastructure.persistence.models import (
    ReportModelSQLAlchemy
)


class ReportMapper:
    @staticmethod
    def to_sqlalchemy(domain: Report) -> ReportModelSQLAlchemy:
        """Converte o modelo de Domínio (Dataclass) para o modelo do SQLAlchemy."""
        if not domain:
            return None

        return ReportModelSQLAlchemy(
            id=domain.id,
            description=domain.description,
            target_entity=domain.target_entity,
            target_id=domain.target_id,
            user_id=domain.user_id,
        )

    @staticmethod
    def to_domain(db_model: ReportModelSQLAlchemy) -> Report:
        """Converte o modelo do SQLAlchemy para a Entidade de Domínio (Dataclass)."""
        if not db_model:
            return None

        return Report(
            id=db_model.id,
            description=db_model.description,
            target_entity=db_model.target_entity,
            target_id=db_model.target_id,
            user_id=db_model.user_id,
        )
