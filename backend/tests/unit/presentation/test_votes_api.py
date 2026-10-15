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
    for status, target_entity, target_id, user_id in [
        ("like", "books", 3, 1),
        ("dislike", "books", 3, 1),
        ("like", "reviews", 3, 2),
    ]:
        response = client.post(
            "/votes",
            json={
                "status": status,
                "target_entity": target_entity,
                "target_id": target_id,
                "user_id": user_id,
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
