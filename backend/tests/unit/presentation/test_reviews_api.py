REVIEW = {
    "rating": 5,
    "comment": "Excelente leitura",
    "user_id": 1,
    "book_id": 1,
}


def test_create_review_defaults_is_spoiler_to_false(client):
    response = client.post("/reviews", json=REVIEW)

    assert response.status_code == 201
    assert response.json()["isSpoiler"] is False


def test_update_review_spoiler(client):
    created = client.post("/reviews", json=REVIEW).json()

    response = client.patch(
        f"/reviews/{created['id']}/spoiler", json={"isSpoiler": True}
    )

    assert response.status_code == 200
    assert response.json()["isSpoiler"] is True
    assert client.get(f"/reviews/{created['id']}").json()["isSpoiler"] is True


def test_update_review_accepts_is_spoiler(client):
    created = client.post("/reviews", json=REVIEW).json()

    rejected = client.put(
        f"/reviews/{created['id']}",
        json={
            "rating": 4,
            "comment": "Review atualizada",
            "isSpoiler": True,
            "user_id": 99,
            "book_id": 99,
        },
    )
    assert rejected.status_code == 422

    response = client.put(
        f"/reviews/{created['id']}",
        json={
            "rating": 4,
            "comment": "Review atualizada",
            "isSpoiler": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["isSpoiler"] is True
    assert response.json()["user_id"] == REVIEW["user_id"]
    assert response.json()["book_id"] == REVIEW["book_id"]


def test_update_unknown_review_returns_404(client):
    response = client.patch("/reviews/999/spoiler", json={"isSpoiler": True})

    assert response.status_code == 404
