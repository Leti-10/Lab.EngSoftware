BOOK = {
    "isbn": "9788535902778",
    "title": "Dom Casmurro",
    "publisher": "Companhia das Letras",
    "authors": ["Machado de Assis"],
    "genre": ["Romance"],
}
LIST = {"name": "Favoritos", "description": "Os que eu mais amo"}


def _other_user_headers(client):
    response = client.post(
        "/auth/register",
        json={"username": "bia", "email": "bia@example.com", "password": "senha123"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_lists_require_login(client):
    assert client.get("/lists").status_code == 401
    assert client.post("/lists", json=LIST).status_code == 401


def test_create_and_list_my_lists(client, auth_headers):
    created = client.post("/lists", json=LIST, headers=auth_headers)

    assert created.status_code == 201
    assert created.json()["books"] == []

    mine = client.get("/lists", headers=auth_headers).json()
    assert [item["name"] for item in mine] == ["Favoritos"]


def test_create_list_with_short_name_returns_422(client, auth_headers):
    response = client.post("/lists", json={**LIST, "name": "ab"}, headers=auth_headers)

    assert response.status_code == 422


def test_duplicate_list_name_returns_409(client, auth_headers):
    client.post("/lists", json=LIST, headers=auth_headers)

    assert client.post("/lists", json=LIST, headers=auth_headers).status_code == 409


def test_add_book_to_list(client, auth_headers):
    book = client.post("/books", json=BOOK, headers=auth_headers).json()
    created = client.post("/lists", json=LIST, headers=auth_headers).json()

    response = client.post(
        f"/lists/{created['id']}/books", json={"book_id": book["id"]}, headers=auth_headers
    )

    assert response.status_code == 200
    assert [b["title"] for b in response.json()["books"]] == ["Dom Casmurro"]


def test_add_same_book_twice_returns_409(client, auth_headers):
    book = client.post("/books", json=BOOK, headers=auth_headers).json()
    created = client.post("/lists", json=LIST, headers=auth_headers).json()
    url = f"/lists/{created['id']}/books"
    client.post(url, json={"book_id": book["id"]}, headers=auth_headers)

    assert client.post(url, json={"book_id": book["id"]}, headers=auth_headers).status_code == 409


def test_add_unknown_book_returns_404(client, auth_headers):
    created = client.post("/lists", json=LIST, headers=auth_headers).json()

    response = client.post(
        f"/lists/{created['id']}/books", json={"book_id": 99}, headers=auth_headers
    )

    assert response.status_code == 404


def test_cannot_change_someone_elses_list(client, auth_headers):
    book = client.post("/books", json=BOOK, headers=auth_headers).json()
    created = client.post("/lists", json=LIST, headers=auth_headers).json()
    intruder = _other_user_headers(client)

    response = client.post(
        f"/lists/{created['id']}/books", json={"book_id": book["id"]}, headers=intruder
    )

    assert response.status_code == 403


def test_private_list_is_hidden_from_others(client, auth_headers):
    created = client.post("/lists", json={**LIST, "private": True}, headers=auth_headers).json()
    other = _other_user_headers(client)

    assert client.get(f"/lists/{created['id']}", headers=other).status_code == 404
    assert client.get(f"/lists/{created['id']}", headers=auth_headers).status_code == 200
