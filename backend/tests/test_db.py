import pytest

from sqlalchemy import select

from src.model.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="teste", email="teste@example.com", password="password123"
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(select(User).where(User.username == "teste"))

        assert user.id == 1
        assert user.username == "teste"
        assert user.email == "teste@example.com"
        assert user.password == "password123"
        assert user.created_at == time
