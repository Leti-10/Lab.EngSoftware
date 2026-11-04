import pytest

from src.application.use_cases import AuthenticateUserUseCase, CreateUserUseCase
from src.domain.exceptions import InvalidCredentialsError
from src.infrastructure.persistence.repositories import InMemoryUserRepository


@pytest.fixture
async def repository():
    repo = InMemoryUserRepository()
    await CreateUserUseCase(repo).execute("leticia", "leticia@example.com", "senha123")
    return repo


@pytest.mark.asyncio
async def test_should_authenticate_with_valid_credentials(repository):
    user = await AuthenticateUserUseCase(repository).execute(
        "leticia@example.com", "senha123"
    )

    assert user.username == "leticia"
    assert user.id == 1


@pytest.mark.asyncio
async def test_should_reject_wrong_password(repository):
    with pytest.raises(InvalidCredentialsError):
        await AuthenticateUserUseCase(repository).execute(
            "leticia@example.com", "errada"
        )


@pytest.mark.asyncio
async def test_should_reject_unknown_email(repository):
    with pytest.raises(InvalidCredentialsError):
        await AuthenticateUserUseCase(repository).execute("x@example.com", "senha123")
