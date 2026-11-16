from src.domain.entities import Report
from src.infrastructure.persistence.models import ReportModelSQLAlchemy
from src.infrastructure.persistence.mappers import ReportMapper


def test_report_mapper_round_trip():
    report = Report(
        id=3,
        user_id=1,
        target_id=2,
        target_entity="user",
        description="Abuso no perfil",
    )

    model = ReportMapper.to_sqlalchemy(report)
    restored = ReportMapper.to_domain(model)

    assert restored == report
    assert model.target_entity == "user"
    assert not ReportModelSQLAlchemy.__table__.foreign_keys
