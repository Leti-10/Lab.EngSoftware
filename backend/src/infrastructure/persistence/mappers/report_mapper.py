from src.domain.entities import Report
from src.infrastructure.persistence.models import ReportModelSQLAlchemy


class ReportMapper:
    @staticmethod
    def to_sqlalchemy(domain: Report) -> ReportModelSQLAlchemy:
        return ReportModelSQLAlchemy(
            id=domain.id,
            user_id=domain.user_id,
            target_id=domain.target_id,
            target_entity=domain.target_entity,
            description=domain.description,
        )

    @staticmethod
    def to_domain(db_model: ReportModelSQLAlchemy) -> Report:
        return Report(
            id=db_model.id,
            user_id=db_model.user_id,
            target_id=db_model.target_id,
            target_entity=db_model.target_entity,
            description=db_model.description,
        )
