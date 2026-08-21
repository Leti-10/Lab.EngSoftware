from src.model.models import User
from sqlalchemy import select
from dataclasses import asdict

def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="teste",
            email="teste@example.com",
            password="password123"
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == "teste"))

        assert asdict(user) == {
            "id": 1,
            "username": "teste",
            "email": "teste@example.com",
            "password": "password123",
            "created_at": time
        }