def register(client, username):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "senha123",
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_readings_require_login(client):
    assert client.get("/readings").status_code == 401
    assert client.put("/readings/1", json={"status": "reading"}).status_code == 401
    assert client.delete("/readings/1").status_code == 401


def test_set_reading_status_creates_and_updates(client, auth_headers):
    created = client.put(
        "/readings/1", json={"status": "reading"}, headers=auth_headers
    )
    updated = client.put("/readings/1", json={"status": "read"}, headers=auth_headers)

    assert created.status_code == 200
    assert created.json()["status"] == "reading"
    assert updated.json()["status"] == "read"
    assert updated.json()["id"] == created.json()["id"]
    assert len(client.get("/readings", headers=auth_headers).json()) == 1


def test_set_reading_status_rejects_unknown_status(client, auth_headers):
    response = client.put(
        "/readings/1", json={"status": "abandoned"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_list_readings_filters_by_book_and_status(client, auth_headers):
    client.put("/readings/1", json={"status": "reading"}, headers=auth_headers)
    client.put("/readings/2", json={"status": "want_to_read"}, headers=auth_headers)

    by_book = client.get("/readings", params={"book_id": 2}, headers=auth_headers)
    by_status = client.get(
        "/readings", params={"status": "reading"}, headers=auth_headers
    )

    assert [item["book_id"] for item in by_book.json()] == [2]
    assert [item["book_id"] for item in by_status.json()] == [1]


def test_readings_are_private_to_each_user(client, auth_headers):
    client.put("/readings/1", json={"status": "reading"}, headers=auth_headers)
    other = register(client, "bia")

    assert client.get("/readings", headers=other).json() == []
    assert client.delete("/readings/1", headers=other).status_code == 404


def test_remove_reading(client, auth_headers):
    client.put("/readings/1", json={"status": "reading"}, headers=auth_headers)

    removed = client.delete("/readings/1", headers=auth_headers)

    assert removed.status_code == 204
    assert client.get("/readings", headers=auth_headers).json() == []
    assert client.delete("/readings/1", headers=auth_headers).status_code == 404
