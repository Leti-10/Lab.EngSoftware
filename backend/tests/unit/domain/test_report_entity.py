import pytest

from src.domain.entities import Report
from src.domain.exceptions import (
    InvalidReportDescriptionError,
    InvalidReportTargetEntityError,
    InvalidReportTargetError,
    InvalidReportUserError,
)


def test_report_accepts_user_as_target():
    report = Report(
        user_id=1,
        target_id=2,
        target_entity="user",
        description="Abuso no perfil",
    )

    assert report.target_entity == "user"
    assert report.target_id == 2


@pytest.mark.parametrize(
    "values, error",
    [
        ({"user_id": 0}, InvalidReportUserError),
        ({"target_id": 0}, InvalidReportTargetError),
        ({"target_entity": " "}, InvalidReportTargetEntityError),
        ({"description": " "}, InvalidReportDescriptionError),
        ({"description": "x" * 1001}, InvalidReportDescriptionError),
    ],
)
def test_report_rejects_invalid_values(values, error):
    arguments = {
        "user_id": 1,
        "target_id": 2,
        "target_entity": "user",
        "description": "Abuso no perfil",
        **values,
    }

    with pytest.raises(error):
        Report(**arguments)
