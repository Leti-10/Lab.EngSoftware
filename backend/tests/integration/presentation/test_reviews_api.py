REVIEW = {
    "rating": 5,
    "comment": "Excelente leitura",
    "book_id": 1,
}


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


def test_create_review_requires_login(client):
    response = client.post("/reviews", json=REVIEW)

    assert response.status_code == 401


def test_create_review_uses_logged_user_and_returns_username(client, auth_headers):
    response = client.post("/reviews", json=REVIEW, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["created_at"]
    assert body["isSpoiler"] is False
    assert body["username"] == "ana"
    assert body["likes"] == 0
    assert body["liked_by_me"] is False


def test_create_review_ignores_user_id_from_body(client, auth_headers):
    response = client.post(
        "/reviews", json={**REVIEW, "user_id": 999}, headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["user_id"] != 999


def test_create_second_review_for_same_book_returns_409(client, auth_headers):
    client.post("/reviews", json=REVIEW, headers=auth_headers)

    response = client.post("/reviews", json=REVIEW, headers=auth_headers)

    assert response.status_code == 409


def test_filter_reviews_by_book_id(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()
    other = register(client, "bia")
    client.post("/reviews", json={**REVIEW, "book_id": 2}, headers=other)

    response = client.get("/reviews", params={"book_id": 2})

    assert response.status_code == 200
    assert [item["username"] for item in response.json()] == ["bia"]
    response = client.get("/reviews", params={"book_id": REVIEW["book_id"]})
    assert response.json()[0]["created_at"] == created["created_at"]


def test_filter_reviews_by_user_id(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()
    other = register(client, "bia")
    client.post("/reviews", json={**REVIEW, "book_id": 2}, headers=other)

    response = client.get("/reviews", params={"user_id": created["user_id"]})

    assert [item["id"] for item in response.json()] == [created["id"]]


def test_update_review_spoiler(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()

    response = client.patch(
        f"/reviews/{created['id']}/spoiler",
        json={"isSpoiler": True},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["isSpoiler"] is True
    assert client.get(f"/reviews/{created['id']}").json()["isSpoiler"] is True


def test_update_review_accepts_is_spoiler(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()

    rejected = client.put(
        f"/reviews/{created['id']}",
        json={
            "rating": 4,
            "comment": "Review atualizada",
            "isSpoiler": True,
            "user_id": 99,
            "book_id": 99,
        },
        headers=auth_headers,
    )
    assert rejected.status_code == 422

    response = client.put(
        f"/reviews/{created['id']}",
        json={"rating": 4, "comment": "Review atualizada", "isSpoiler": True},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["isSpoiler"] is True
    assert response.json()["user_id"] == created["user_id"]
    assert response.json()["book_id"] == REVIEW["book_id"]
    assert response.json()["created_at"] == created["created_at"]


def test_update_review_of_another_user_returns_403(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()
    other = register(client, "bia")

    put = client.put(f"/reviews/{created['id']}", json={"rating": 1}, headers=other)
    patch = client.patch(
        f"/reviews/{created['id']}/spoiler", json={"isSpoiler": True}, headers=other
    )

    assert put.status_code == 403
    assert patch.status_code == 403


def test_update_review_requires_login(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()

    response = client.put(f"/reviews/{created['id']}", json={"rating": 3})

    assert response.status_code == 401


def test_update_unknown_review_returns_404(client, auth_headers):
    response = client.patch(
        "/reviews/999/spoiler", json={"isSpoiler": True}, headers=auth_headers
    )

    assert response.status_code == 404


def test_review_reports_likes_and_whether_viewer_liked(client, auth_headers):
    created = client.post("/reviews", json=REVIEW, headers=auth_headers).json()
    other = register(client, "bia")
    vote = client.post(
        "/votes",
        json={"status": "like", "target_entity": "reviews", "target_id": created["id"]},
        headers=other,
    ).json()

    as_author = client.get(f"/reviews/{created['id']}", headers=auth_headers).json()
    as_voter = client.get(f"/reviews/{created['id']}", headers=other).json()
    anonymous = client.get(f"/reviews/{created['id']}").json()

    assert as_author["likes"] == 1 and as_author["liked_by_me"] is False
    assert as_voter["liked_by_me"] is True
    assert as_voter["like_vote_id"] == vote["id"]
    assert anonymous["likes"] == 1 and anonymous["liked_by_me"] is False
