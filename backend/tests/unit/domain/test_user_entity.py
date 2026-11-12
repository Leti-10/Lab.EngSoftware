from datetime import UTC, datetime

import pytest

from src.domain.entities import User


@pytest.mark.parametrize(
    "username, email, password, expected_error",
    [
        ("", "capivara@example.com", "anypassword", "Username não pode ser vazio"),
        (
            "ca",
            "capivara@example.com",
            "anypassword",
            "Username deve ter pelo menos 3 caracteres",
        ),
        ("capivara", "email-sem-formato", "anypassword", "E-mail inválido"),
        ("capivara", "capivara@example.com", "", "Password não pode ser vazio"),
    ],
)
def test_should_raise_error_when_user_data_is_invalid(
    username, email, password, expected_error
):
    with pytest.raises(ValueError, match=expected_error):
        User(
            username=username,
            email=email,
            password=password,
            role="user",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_should_assign_default_role_when_not_provided():
    user = User(
        username="capivara",
        email="capivara@example.com",
        password="hashed-password",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert user.role == "user"


def test_should_assign_utc_timezone_to_default_created_at():
    user = User(
        username="capivara",
        email="capivara@example.com",
        password="hashed-password",
    )

    assert user.created_at.tzinfo is UTC
