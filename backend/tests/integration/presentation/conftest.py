import pytest
from fastapi.testclient import TestClient

from src.domain.enums.enums import EnumVoteTarget
from src.infrastructure.persistence.repositories import (
    InMemoryBookListRepository,
    InMemoryBookRepository,
    InMemoryCommentRepository,
    InMemoryFollowRepository,
    InMemoryNotificationPreferenceRepository,
    InMemoryNotificationRepository,
    InMemoryReportRepository,
    InMemoryReadingRepository,
    InMemoryReviewRepository,
    InMemoryUserRepository,
    InMemoryVoteRepository,
)
from src.infrastructure.security.token_service import ACCESS_TOKEN_COOKIE_NAME
from src.presentation.api.dependencies import (
    get_comment_repository,
    get_follow_repository,
    get_notification_preference_repository,
    get_notification_repository,
    get_user_repository,
)
from src.presentation.api.main import app
from src.presentation.api.routes.book_list_router import get_book_list_repository
from src.presentation.api.routes.book_router import get_book_repository
from src.presentation.api.routes.report_router import get_report_repository
from src.presentation.api.routes.reading_router import get_reading_repository
from src.presentation.api.routes.review_router import get_review_repository
from src.presentation.api.routes.vote_router import get_vote_repository


@pytest.fixture
def client():
    users = InMemoryUserRepository()
    books = InMemoryBookRepository()
    lists = InMemoryBookListRepository()
    reviews = InMemoryReviewRepository()
    votes = InMemoryVoteRepository(
        user_names={1: "ana"},
        target_names={
            (EnumVoteTarget.BOOK, 3): "Dom Casmurro",
            (EnumVoteTarget.REVIEW, 3): "Excelente leitura",
            (EnumVoteTarget.LIST, 1): "Favoritos",
        },
    )
    comments = InMemoryCommentRepository()
    follows = InMemoryFollowRepository()
    notifications = InMemoryNotificationRepository()
    preferences = InMemoryNotificationPreferenceRepository()
    reports = InMemoryReportRepository()
    app.dependency_overrides[get_comment_repository] = lambda: comments
    app.dependency_overrides[get_follow_repository] = lambda: follows
    app.dependency_overrides[get_notification_repository] = lambda: notifications
    app.dependency_overrides[get_notification_preference_repository] = lambda: (
        preferences
    )
    app.dependency_overrides[get_user_repository] = lambda: users
    app.dependency_overrides[get_book_repository] = lambda: books
    app.dependency_overrides[get_book_list_repository] = lambda: lists
    app.dependency_overrides[get_report_repository] = lambda: reports
    readings = InMemoryReadingRepository()
    app.dependency_overrides[get_reading_repository] = lambda: readings
    app.dependency_overrides[get_review_repository] = lambda: reviews
    app.dependency_overrides[get_vote_repository] = lambda: votes
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "ana",
            "email": "ana.fixture@example.com",
            "password": "senha123",
        },
    )
    token = response.cookies[ACCESS_TOKEN_COOKIE_NAME]
    client.cookies.clear()
    return {"Authorization": f"Bearer {token}"}
