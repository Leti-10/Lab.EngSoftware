def test_update_profile_requires_login(client):
    response = client.put("/auth/me", json={"bio": "Oi"})

    assert response.status_code == 401


def test_new_account_has_empty_profile(client, auth_headers):
    body = client.get("/auth/me", headers=auth_headers).json()

    assert body["bio"] is None
    assert body["avatar_url"] is None
    assert body["cover_url"] is None


def test_update_profile_saves_bio_avatar_and_cover(client, auth_headers):
    response = client.put(
        "/auth/me",
        json={
            "bio": "  Leitora de mangás  ",
            "avatar_url": "https://exemplo.com/eu.png",
            "cover_url": "http://exemplo.com/capa.jpg",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["bio"] == "Leitora de mangás"
    assert response.json()["avatar_url"] == "https://exemplo.com/eu.png"
    assert client.get("/auth/me", headers=auth_headers).json()["cover_url"] == (
        "http://exemplo.com/capa.jpg"
    )


def test_update_profile_clears_empty_fields(client, auth_headers):
    client.put("/auth/me", json={"bio": "Oi"}, headers=auth_headers)

    response = client.put(
        "/auth/me", json={"bio": "", "avatar_url": "  "}, headers=auth_headers
    )

    assert response.json()["bio"] is None
    assert response.json()["avatar_url"] is None


def test_update_profile_rejects_invalid_url(client, auth_headers):
    response = client.put(
        "/auth/me", json={"avatar_url": "javascript:alert(1)"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_update_profile_rejects_long_bio(client, auth_headers):
    response = client.put("/auth/me", json={"bio": "a" * 301}, headers=auth_headers)

    assert response.status_code == 422
