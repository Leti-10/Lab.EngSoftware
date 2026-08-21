from http import HTTPStatus

def test_create_user(client):
    response = client.post("/user", 
                json={"username": "teste",
                      "email": "teste@example.com",
                      "password": "teste123"})

    assert response.status_code == HTTPStatus.CREATED

def test_get_users(client, user, token):
    response = client.get("/user", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "id": 1,
                "username": "teste",
                "email": "teste@example.com"
            }
        ]
    }

def test_update_user(client, user, token):
    response = client.put("/user/1", 
                headers={"Authorization": f"Bearer {token}"},
                json={"username": "teste_atualizado",
                      "email": "teste_atualizado@example.com",
                      "password": "teste123"})
    assert response.status_code == HTTPStatus.OK

def test_delete_user(client, user, token):
    response = client.delete("/user/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.NO_CONTENT

def test_get_token(client, user):
    response = client.post("/auth", 
                data={
                    "username": user.email,
                    "password": user.clean_password
                })
    assert response.status_code == HTTPStatus.OK
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()