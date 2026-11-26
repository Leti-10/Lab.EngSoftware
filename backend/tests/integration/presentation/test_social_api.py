BOOK = {
    "isbn": "9788535902778",
    "title": "Dom Casmurro",
    "publisher": "Companhia",
    "authors": ["Machado de Assis"],
    "genre": ["Romance"],
    "theme": [],
}
OTHER_BOOK = {
    "isbn": "9788535914849",
    "title": "Torto Arado",
    "publisher": "Todavia",
    "authors": ["Itamar Vieira Junior"],
    "genre": ["Romance"],
    "theme": [],
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
    body = response.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["id"]


def make_book(client, headers, payload=BOOK):
    return client.post("/books", json=payload, headers=headers).json()["id"]


def make_review(client, headers, book_id, rating=5):
    return client.post(
        "/reviews", json={"rating": rating, "book_id": book_id}, headers=headers
    ).json()["id"]


def test_comments_are_listed_publicly_and_need_login_to_write(client, auth_headers):
    book_id = make_book(client, auth_headers)
    review_id = make_review(client, auth_headers, book_id)
    bia, _ = register(client, "bia")

    assert (
        client.post(f"/reviews/{review_id}/comments", json={"text": "Oi"}).status_code
        == 401
    )
    created = client.post(
        f"/reviews/{review_id}/comments", json={"text": "  Concordo  "}, headers=bia
    )
    listed = client.get(f"/reviews/{review_id}/comments")

    assert created.status_code == 201
    assert listed.json()[0]["text"] == "Concordo"
    assert listed.json()[0]["username"] == "bia"


def test_comment_validation_and_missing_review(client, auth_headers):
    book_id = make_book(client, auth_headers)
    review_id = make_review(client, auth_headers, book_id)

    empty = client.post(
        f"/reviews/{review_id}/comments", json={"text": "  "}, headers=auth_headers
    )
    long = client.post(
        f"/reviews/{review_id}/comments", json={"text": "a" * 501}, headers=auth_headers
    )
    missing = client.post(
        "/reviews/99/comments", json={"text": "Oi"}, headers=auth_headers
    )

    assert empty.status_code == 422
    assert long.status_code == 422
    assert missing.status_code == 404


def test_only_author_deletes_comment(client, auth_headers):
    book_id = make_book(client, auth_headers)
    review_id = make_review(client, auth_headers, book_id)
    bia, _ = register(client, "bia")
    comment = client.post(
        f"/reviews/{review_id}/comments", json={"text": "Oi"}, headers=bia
    ).json()

    assert (
        client.delete(f"/comments/{comment['id']}", headers=auth_headers).status_code
        == 403
    )
    assert client.delete(f"/comments/{comment['id']}", headers=bia).status_code == 204
    assert client.delete(f"/comments/{comment['id']}", headers=bia).status_code == 404


def test_follow_user_counts_and_notifies(client, auth_headers):
    bia, bia_id = register(client, "bia")

    followed = client.put(f"/follows/users/{bia_id}", headers=auth_headers)
    again = client.put(f"/follows/users/{bia_id}", headers=auth_headers)
    status = client.get(f"/follows/users/{bia_id}", headers=auth_headers)
    notifications = client.get("/notifications", headers=bia).json()

    assert followed.json() == {"following": True, "followers": 1}
    assert again.json()["followers"] == 1
    assert status.json()["following"] is True
    assert client.get(f"/follows/users/{bia_id}").json() == {
        "following": False,
        "followers": 1,
    }
    assert [item["type"] for item in notifications["items"]] == ["follow"]
    assert notifications["items"][0]["actor_username"] == "ana"


def test_follow_rules(client, auth_headers):
    _, ana_id = register(client, "outra")
    me = client.get("/auth/me", headers=auth_headers).json()["id"]

    assert client.put(f"/follows/users/{me}", headers=auth_headers).status_code == 422
    assert client.put("/follows/users/999", headers=auth_headers).status_code == 404
    assert client.put(f"/follows/users/{ana_id}").status_code == 401


def test_unfollow_user(client, auth_headers):
    _, bia_id = register(client, "bia")
    client.put(f"/follows/users/{bia_id}", headers=auth_headers)

    response = client.delete(f"/follows/users/{bia_id}", headers=auth_headers)

    assert response.json() == {"following": False, "followers": 0}


def test_follow_public_list_but_not_private_one(client, auth_headers):
    bia, bia_id = register(client, "bia")
    public = client.post(
        "/lists",
        json={"name": "Publica", "description": "x", "private": False},
        headers=bia,
    ).json()
    private = client.post(
        "/lists",
        json={"name": "Secreta", "description": "x", "private": True},
        headers=bia,
    ).json()

    assert (
        client.put(f"/follows/lists/{public['id']}", headers=auth_headers).json()[
            "followers"
        ]
        == 1
    )
    assert (
        client.put(f"/follows/lists/{private['id']}", headers=auth_headers).status_code
        == 404
    )
    mine = client.get("/follows", params={"type": "lists"}, headers=auth_headers).json()
    assert mine == [{"target_type": "lists", "target_id": public["id"]}]


def test_public_profile_shows_counts_and_public_lists(client, auth_headers):
    bia, bia_id = register(client, "bia")
    client.put(f"/follows/users/{bia_id}", headers=auth_headers)
    client.put("/auth/me", json={"bio": "Oi"}, headers=bia)
    client.post("/lists", json={"name": "Publica", "description": "x"}, headers=bia)
    client.post(
        "/lists",
        json={"name": "Secreta", "description": "x", "private": True},
        headers=bia,
    )

    profile = client.get(f"/users/{bia_id}", headers=auth_headers).json()
    lists = client.get(f"/users/{bia_id}/lists").json()

    assert profile["followers"] == 1
    assert profile["is_following"] is True
    assert profile["bio"] == "Oi"
    assert [item["name"] for item in lists] == ["Publica"]
    assert client.get("/users/999").status_code == 404


def test_public_list_includes_books(client, auth_headers):
    user_id = client.get("/auth/me", headers=auth_headers).json()["id"]
    book_id = make_book(client, auth_headers)
    created = client.post(
        "/lists",
        json={"name": "Favoritos", "description": "Minhas obras favoritas"},
        headers=auth_headers,
    ).json()
    client.post(
        f"/lists/{created['id']}/books",
        json={"book_id": book_id},
        headers=auth_headers,
    )
    response = client.get(f"/users/{user_id}/lists")

    assert response.status_code == 200
    assert [book["id"] for book in response.json()[0]["books"]] == [book_id]


def test_like_and_comment_notify_the_review_author_once_per_action(
    client, auth_headers
):
    book_id = make_book(client, auth_headers)
    review_id = make_review(client, auth_headers, book_id)
    bia, _ = register(client, "bia")

    client.post(
        "/votes",
        json={"status": "like", "target_entity": "reviews", "target_id": review_id},
        headers=bia,
    )
    client.post(f"/reviews/{review_id}/comments", json={"text": "Oi"}, headers=bia)
    client.post(
        f"/reviews/{review_id}/comments", json={"text": "Eu"}, headers=auth_headers
    )

    result = client.get("/notifications", headers=auth_headers).json()

    assert result["unread"] == 2
    assert sorted(item["type"] for item in result["items"]) == ["comment", "like"]
    assert all(item["book_id"] == book_id for item in result["items"])


def test_notifications_can_be_marked_as_read(client, auth_headers):
    bia, bia_id = register(client, "bia")
    client.put(f"/follows/users/{bia_id}", headers=auth_headers)
    first = client.get("/notifications", headers=bia).json()["items"][0]

    assert (
        client.patch(f"/notifications/{first['id']}/read", headers=bia).status_code
        == 204
    )
    assert client.get("/notifications", headers=bia).json()["unread"] == 0
    assert client.patch("/notifications/99/read", headers=bia).status_code == 404
    client.delete(f"/follows/users/{bia_id}", headers=auth_headers)
    client.put(f"/follows/users/{bia_id}", headers=auth_headers)
    assert client.get("/notifications", headers=bia).json()["unread"] == 1
    assert client.post("/notifications/read", headers=bia).status_code == 204
    assert client.get("/notifications", headers=bia).json()["unread"] == 0


def test_notification_preferences_silence_notifications(client, auth_headers):
    bia, bia_id = register(client, "bia")

    defaults = client.get("/notifications/preferences", headers=bia).json()
    client.put(
        "/notifications/preferences",
        json={"likes": True, "comments": True, "follows": False},
        headers=bia,
    )
    client.put(f"/follows/users/{bia_id}", headers=auth_headers)

    assert defaults == {"likes": True, "comments": True, "follows": True}
    assert (
        client.get("/notifications/preferences", headers=bia).json()["follows"] is False
    )
    assert client.get("/notifications", headers=bia).json()["items"] == []


def test_feed_shows_reviews_of_followed_users_newest_first(client, auth_headers):
    bia, bia_id = register(client, "bia")
    book_a = make_book(client, bia)
    book_b = make_book(client, bia, OTHER_BOOK)
    make_review(client, bia, book_a, rating=3)
    make_review(client, bia, book_b, rating=5)
    carol, _ = register(client, "carol")
    make_review(client, carol, book_a, rating=1)

    assert client.get("/feed", headers=auth_headers).json() == []
    client.put(f"/follows/users/{bia_id}", headers=auth_headers)
    feed = client.get("/feed", headers=auth_headers).json()

    assert [item["book_title"] for item in feed] == ["Torto Arado", "Dom Casmurro"]
    assert {item["username"] for item in feed} == {"bia"}
    assert client.get("/feed").status_code == 401


def test_recommendations_follow_taste_and_skip_seen_books(client, auth_headers):
    mangas = {
        **BOOK,
        "isbn": "9781111111111",
        "title": "Naruto 1",
        "authors": ["Kishimoto"],
        "genre": ["Mangá", "Ação"],
    }
    more_mangas = {
        **BOOK,
        "isbn": "9782222222222",
        "title": "Naruto 2",
        "authors": ["Kishimoto"],
        "genre": ["Mangá", "Ação"],
    }
    romance = {
        **BOOK,
        "isbn": "9783333333333",
        "title": "Outro Romance",
        "authors": ["Alguém"],
        "genre": ["Romance"],
    }
    loved = make_book(client, auth_headers, mangas)
    next_one = make_book(client, auth_headers, more_mangas)
    make_book(client, auth_headers, romance)

    assert client.get("/recommendations", headers=auth_headers).json() == []
    make_review(client, auth_headers, loved, rating=5)
    result = client.get("/recommendations", headers=auth_headers).json()

    assert [item["book"]["id"] for item in result] == [next_one]
    assert result[0]["reason"] == "Porque você gosta de Kishimoto"
    client.put(f"/readings/{next_one}", json={"status": "read"}, headers=auth_headers)
    assert client.get("/recommendations", headers=auth_headers).json() == []
