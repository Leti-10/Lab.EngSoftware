def _register(client, email="ana@example.com"):
    return client.post(
        "/auth/register",
        json={"username": "ana", "email": email, "password": "senha123"},
    )


def test_register_returns_token_and_user(client):
    response = _register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "ana@example.com"
    assert "password" not in body["user"]


def test_register_duplicate_email_returns_409(client):
    _register(client)

    assert _register(client).status_code == 409


def test_login_and_me_flow(client):
    _register(client)

    login = client.post("/auth/login", json={"email": "ana@example.com", "password": "senha123"})
    assert login.status_code == 200

    token = login.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "ana"


def test_login_with_wrong_password_returns_401(client):
    _register(client)

    response = client.post("/auth/login", json={"email": "ana@example.com", "password": "errada"})

    assert response.status_code == 401


def test_me_without_token_returns_401(client):
    assert client.get("/auth/me").status_code == 401
