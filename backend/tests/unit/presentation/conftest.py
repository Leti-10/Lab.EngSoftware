import pytest
from fastapi.testclient import TestClient

from src.infrastructure.persistence.repositories import (
    InMemoryBookRepository,
    InMemoryUserRepository,
)
from src.presentation.api.dependencies import get_user_repository
from src.presentation.api.main import app
from src.presentation.api.routes.book_router import get_book_m_repository


@pytest.fixture
def client():
    users = InMemoryUserRepository()
    books = InMemoryBookRepository()
    app.dependency_overrides[get_user_repository] = lambda: users
    app.dependency_overrides[get_book_m_repository] = lambda: books
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/register",
        json={"username": "ana", "email": "ana.fixture@example.com", "password": "senha123"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
