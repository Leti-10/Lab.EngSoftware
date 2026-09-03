import pytest

from sqlalchemy import select

from dataclasses import asdict

from src.model.models import User
from src.model.report_model import Report

@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="teste", email="teste@example.com", password="password123"
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(select(User).where(User.username == "teste"))

        assert asdict(user) == {
            "id": 1,
            "username": "teste",
            "email": "teste@example.com",
            "password": "password123",
            "created_at": time,
        }

@pytest.mark.asyncio
async def test_create_user(session):
        new_report = Report(
            description="teste", target_entity="books", target_id="1", user_id="1"
        )

        session.add(new_report)
        await session.commit()

        report = await session.scalar(select(Report).where(Report.id == "1"))

        assert asdict(report) == {
            "id": 1,
            "description": "teste",
            "target_entity": "books",
            "target_id": "1",
            "user_id": "1"
        }