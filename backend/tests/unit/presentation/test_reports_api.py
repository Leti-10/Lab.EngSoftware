from sqlalchemy.exc import IntegrityError

from src.domain.entities import Report
from src.presentation.api.routes.report_router import get_report_repository


class InMemoryReportRepository:
    def __init__(self):
        self.reports = []

    async def save(self, report: Report) -> Report:
        report.id = len(self.reports) + 1
        self.reports.append(report)
        return report

    async def get_by_id(self, report_id: int) -> Report | None:
        return next(
            (report for report in self.reports if report.id == report_id), None
        )

    async def find_by_filter(
        self,
        user_id: int | None = None,
        target_id: int | None = None,
        target_entity: str | None = None,
    ) -> list[Report]:
        return [
            report
            for report in self.reports
            if (user_id is None or report.user_id == user_id)
            and (target_id is None or report.target_id == target_id)
            and (target_entity is None or report.target_entity == target_entity)
        ]


def test_create_report_targeting_user(client, auth_headers):
    repository = InMemoryReportRepository()
    from src.presentation.api.main import app

    app.dependency_overrides[get_report_repository] = lambda: repository

    response = client.post(
        "/reports",
        json={
            "target_id": 2,
            "target_entity": "user",
            "description": "Abuso no perfil",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "target_id": 2,
        "target_entity": "user",
        "description": "Abuso no perfil",
    }


def test_create_report_rejects_duplicate_user_target(client, auth_headers):
    repository = InMemoryReportRepository()
    from src.presentation.api.main import app

    app.dependency_overrides[get_report_repository] = lambda: repository

    payload = {
        "target_id": 2,
        "target_entity": "user",
        "description": "Abuso no perfil",
    }
    first = client.post("/reports", json=payload, headers=auth_headers)
    duplicate = client.post(
        "/reports",
        json={**payload, "description": "Outra denúncia sobre o mesmo perfil"},
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_report_routes_get_by_id_and_filter(client, auth_headers):
    repository = InMemoryReportRepository()
    from src.presentation.api.main import app

    app.dependency_overrides[get_report_repository] = lambda: repository
    client.post(
        "/reports",
        json={
            "target_id": 2,
            "target_entity": "user",
            "description": "Abuso no perfil",
        },
        headers=auth_headers,
    )

    found = client.get("/reports/1", headers=auth_headers)
    filtered = client.get(
        "/reports", params={"target_entity": "user"}, headers=auth_headers
    )
    missing = client.get("/reports/999", headers=auth_headers)

    assert found.status_code == 200
    assert found.json()["target_entity"] == "user"
    assert len(filtered.json()) == 1
    assert missing.status_code == 404


def test_create_report_rejects_invalid_target(client, auth_headers):
    response = client.post(
        "/reports",
        json={
            "target_id": 0,
            "target_entity": "user",
            "description": "Abuso no perfil",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_report_routes_require_authentication(client):
    assert client.post(
        "/reports",
        json={
            "target_id": 2,
            "target_entity": "user",
            "description": "Abuso no perfil",
        },
    ).status_code == 401
    assert client.get("/reports/1").status_code == 401
    assert client.get("/reports").status_code == 401


def test_create_report_rejects_user_id_in_payload(client, auth_headers):
    response = client.post(
        "/reports",
        json={
            "user_id": 99,
            "target_id": 2,
            "target_entity": "user",
            "description": "Abuso no perfil",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_report_handles_repository_integrity_error(client, auth_headers):
    class FailingReportRepository(InMemoryReportRepository):
        async def save(self, report: Report) -> Report:
            raise IntegrityError("INSERT", {}, Exception("constraint violation"))

    from src.presentation.api.main import app

    app.dependency_overrides[get_report_repository] = lambda: FailingReportRepository()

    response = client.post(
        "/reports",
        json={
            "target_id": 2,
            "target_entity": "user",
            "description": "Abuso no perfil",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
