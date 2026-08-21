from http import HTTPStatus

from jwt import decode

from src.security import create_access_token
from src.settings import Settings

settings = Settings()

def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["test"] == data["test"]
    assert "exp" in decoded

def test_jwt_invalid_token(client):
    response = client.delete("/user/1", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}