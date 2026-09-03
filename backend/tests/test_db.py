import pytest

from sqlalchemy import select

from dataclasses import asdict

from src.model.models import User
from src.model.list_model import List

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

async def test_create_list(session):
    new_list = List(
        name="teste", description="exemplo", isPrivate=True
    )

    session.add(new_list)
    await session.commit()

    list = await session.scalar(select(List).where(List.name == "teste"))

    assert asdict(list) == {
        "id": 1,
        "name": "teste",
        "description": "exemplo",
        "isPrivate": True
    }