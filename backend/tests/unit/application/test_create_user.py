import pytest
from src.application.use_cases.user.create_user import CreateUserUseCase
from src.infrastructure.persistence.repositories.inmemory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def user_repository():
    return InMemoryUserRepository()


@pytest.fixture
def create_user_use_case(user_repository):
    return CreateUserUseCase(user_repository)


def test_should_create_user_successfully(create_user_use_case):

    username = "testuser"
    email = "testuser@example.com"
    password = "testpassword"

    created_user = create_user_use_case.execute(username, email, password)

    assert created_user.username == username
    assert created_user.email == email
    assert created_user.role == "user"


def test_should_raise_error_when_username_is_empty(create_user_use_case):
    username = ""
    email = "testuser@example.com"
    password = "testpassword"

    with pytest.raises(ValueError, match="Username não pode ser vazio"):
        create_user_use_case.execute(username, email, password)


def test_should_raise_error_when_email_exists(create_user_use_case):
    username = "testuser"
    email = "testuser@example.com"
    password = "testpassword"

    create_user_use_case.execute(username, email, password)

    username2 = "testuser2"
    email2 = "testuser@example.com"
    password2 = "testpassword2"

    with pytest.raises(ValueError, match="E-mail já cadastrado"):
        create_user_use_case.execute(username2, email2, password2)
