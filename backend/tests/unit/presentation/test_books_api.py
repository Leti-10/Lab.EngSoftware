BOOK = {
    "isbn": "9788535902778",
    "title": "Dom Casmurro",
    "publisher": "Companhia das Letras",
    "authors": ["Machado de Assis"],
    "genre": ["Romance"],
}


def test_create_book_requires_login(client):
    assert client.post("/books", json=BOOK).status_code == 401


def test_create_book_returns_201(client, auth_headers):
    response = client.post("/books", json=BOOK, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Dom Casmurro"
    assert body["authors"] == ["Machado de Assis"]


def test_create_book_with_duplicated_isbn_returns_409(client, auth_headers):
    client.post("/books", json=BOOK, headers=auth_headers)

    response = client.post("/books", json=BOOK, headers=auth_headers)

    assert response.status_code == 409


def test_create_book_with_invalid_isbn_returns_422(client, auth_headers):
    response = client.post("/books", json={**BOOK, "isbn": "123"}, headers=auth_headers)

    assert response.status_code == 422
