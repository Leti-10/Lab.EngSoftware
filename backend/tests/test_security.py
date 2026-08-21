from http import HTTPStatus

from src.security import create_access_token, SECRET_KEY, ALGORITHM
from jwt import decode

def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["test"] == data["test"]
    assert "exp" in decoded

def test_jwt_invalid_token(client):
    response = client.delete("/user/1", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}