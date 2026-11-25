def test_vote_endpoints_require_authentication(client):
    payload = {
        "status": "like",
        "target_entity": "books",
        "target_id": 3,
        "user_id": 1,
    }

    assert client.post("/votes", json=payload).status_code == 401
    assert client.get("/votes").status_code == 401
    assert client.get("/votes/1").status_code == 401
    assert client.delete("/votes/1").status_code == 401
    assert client.get("/votes/favorites").status_code == 401
    assert client.put("/votes/favorites/1").status_code == 401
    assert client.delete("/votes/favorites/1").status_code == 401


def test_create_vote_returns_201(client, auth_headers):
    response = client.post(
        "/votes",
        json={
            "status": "like",
            "target_entity": "books",
            "target_id": 3,
            "user_id": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "status": "like",
        "target_entity": "books",
        "target_id": 3,
        "user_id": 1,
    }
    assert client.get("/votes/1", headers=auth_headers).json() == response.json()


def test_create_vote_rejects_duplicate_user_target(client, auth_headers):
    payload = {
        "status": "like",
        "target_entity": "books",
        "target_id": 3,
    }
    first = client.post("/votes", json=payload, headers=auth_headers)
    duplicate = client.post(
        "/votes",
        json={**payload, "status": "dislike"},
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_create_vote_rejects_invalid_input(client, auth_headers):
    response = client.post(
        "/votes",
        json={
            "status": "",
            "target_entity": "authors",
            "target_id": 0,
            "user_id": 0,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_vote_rejects_blank_status(client, auth_headers):
    response = client.post(
        "/votes",
        json={
            "status": "   ",
            "target_entity": "books",
            "target_id": 3,
            "user_id": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_get_vote_returns_404_when_missing(client, auth_headers):
    assert client.get("/votes/999", headers=auth_headers).status_code == 404


def test_delete_vote_returns_204_and_removes_vote(client, auth_headers):
    created = client.post(
        "/votes",
        json={
            "status": "like",
            "target_entity": "books",
            "target_id": 3,
            "user_id": 1,
        },
        headers=auth_headers,
    )

    response = client.delete(
        f"/votes/{created.json()['id']}", headers=auth_headers
    )

    assert response.status_code == 204
    assert client.get("/votes/1", headers=auth_headers).status_code == 404


def test_delete_unknown_vote_returns_404(client, auth_headers):
    assert client.delete("/votes/999", headers=auth_headers).status_code == 404


def test_filter_votes_by_user_and_target_names(client, auth_headers):
    for status, target_entity, target_id in [
        ("like", "books", 3),
        ("like", "reviews", 3),
    ]:
        response = client.post(
            "/votes",
            json={
                "status": status,
                "target_entity": target_entity,
                "target_id": target_id,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get(
        "/votes",
        params={
            "status": "like",
            "user_name": "ana",
            "target_type": "books",
            "target_name": "Dom Casmurro",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["target_entity"] == "books"


def test_filter_votes_by_list_name(client, auth_headers):
    response = client.post(
        "/votes",
        json={
            "status": "like",
            "target_entity": "lists",
            "target_id": 1,
            "user_id": 1,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201

    response = client.get(
        "/votes",
        params={"target_type": "lists", "target_name": "Favoritos"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_favorites_create_list_and_remove_book(client, auth_headers):
    created_book = client.post(
        "/books",
        headers=auth_headers,
        json={
            "isbn": "9788542603835",
            "title": "One Piece",
            "publisher": "Panini",
            "authors": ["Eiichiro Oda"],
            "genre": ["Mangá"],
            "theme": [],
        },
    )
    assert created_book.status_code == 201
    book_id = created_book.json()["id"]
    existing_vote = client.post(
        "/votes",
        headers=auth_headers,
        json={
            "status": "like",
            "target_entity": "books",
            "target_id": book_id,
        },
    )
    assert existing_vote.status_code == 201

    assert (
        client.put(f"/votes/favorites/{book_id}", headers=auth_headers).status_code
        == 204
    )
    assert (
        client.get(
            f"/votes/{existing_vote.json()['id']}", headers=auth_headers
        ).json()["status"]
        == "favorite"
    )
    assert (
        client.put(f"/votes/favorites/{book_id}", headers=auth_headers).status_code
        == 204
    )
    assert client.get("/votes/favorites", headers=auth_headers).json() == [
        created_book.json()
    ]

    assert (
        client.delete(f"/votes/favorites/{book_id}", headers=auth_headers).status_code
        == 204
    )
    assert client.get("/votes/favorites", headers=auth_headers).json() == []
    assert client.put("/votes/favorites/999", headers=auth_headers).status_code == 404


def test_user_cannot_read_or_delete_another_users_vote(client, auth_headers):
    created = client.post(
        "/votes",
        json={"status": "like", "target_entity": "books", "target_id": 3},
        headers=auth_headers,
    )
    assert created.status_code == 201
    vote_id = created.json()["id"]

    other_user = client.post(
        "/auth/register",
        json={
            "username": "other",
            "email": "other@example.com",
            "password": "senha123",
        },
    )
    other_headers = {
        "Authorization": f"Bearer {other_user.json()['access_token']}"
    }

    assert client.get(f"/votes/{vote_id}", headers=other_headers).status_code == 404
    assert client.delete(f"/votes/{vote_id}", headers=other_headers).status_code == 404
    assert client.get("/votes", headers=other_headers).json() == []
