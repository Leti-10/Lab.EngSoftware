import pytest

from src.application.use_cases import AuthenticateUserUseCase, CreateUserUseCase
from src.domain.exceptions import InvalidCredentialsError
from src.infrastructure.persistence.repositories import InMemoryUserRepository


@pytest.fixture
def repository():
    repo = InMemoryUserRepository()
    CreateUserUseCase(repo).execute("leticia", "leticia@example.com", "senha123")
    return repo


def test_should_authenticate_with_valid_credentials(repository):
    user = AuthenticateUserUseCase(repository).execute("leticia@example.com", "senha123")

    assert user.username == "leticia"
    assert user.id == 1


def test_should_reject_wrong_password(repository):
    with pytest.raises(InvalidCredentialsError):
        AuthenticateUserUseCase(repository).execute("leticia@example.com", "errada")


def test_should_reject_unknown_email(repository):
    with pytest.raises(InvalidCredentialsError):
        AuthenticateUserUseCase(repository).execute("x@example.com", "senha123")
