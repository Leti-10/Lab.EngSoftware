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


def test_list_books_is_public_and_filters(client, auth_headers):
    client.post("/books", json=BOOK, headers=auth_headers)
    client.post(
        "/books",
        json={**BOOK, "isbn": "9788542603835", "title": "One Piece", "genre": ["Mangá"]},
        headers=auth_headers,
    )

    everything = client.get("/books")
    searched = client.get("/books", params={"q": "casmurro"})
    by_genre = client.get("/books", params={"genre": "Mangá"})

    assert [b["title"] for b in everything.json()] == ["Dom Casmurro", "One Piece"]
    assert [b["title"] for b in searched.json()] == ["Dom Casmurro"]
    assert [b["title"] for b in by_genre.json()] == ["One Piece"]


def test_get_book_returns_details(client, auth_headers):
    created = client.post("/books", json=BOOK, headers=auth_headers).json()

    response = client.get(f"/books/{created['id']}")

    assert response.status_code == 200
    assert response.json()["isbn"] == BOOK["isbn"]


def test_get_unknown_book_returns_404(client):
    assert client.get("/books/999").status_code == 404


def test_update_book(client, auth_headers):
    created = client.post("/books", json=BOOK, headers=auth_headers).json()

    response = client.put(
        f"/books/{created['id']}", json={**BOOK, "title": "Novo título"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Novo título"
    assert client.get(f"/books/{created['id']}").json()["title"] == "Novo título"


def test_update_requires_login(client, auth_headers):
    created = client.post("/books", json=BOOK, headers=auth_headers).json()

    assert client.put(f"/books/{created['id']}", json=BOOK).status_code == 401


def test_update_with_isbn_of_another_book_returns_409(client, auth_headers):
    client.post("/books", json=BOOK, headers=auth_headers)
    other_isbn = {**BOOK, "isbn": "9788542603835"}
    other = client.post("/books", json=other_isbn, headers=auth_headers).json()

    response = client.put(f"/books/{other['id']}", json=BOOK, headers=auth_headers)

    assert response.status_code == 409


def test_update_unknown_book_returns_404(client, auth_headers):
    assert client.put("/books/99", json=BOOK, headers=auth_headers).status_code == 404


def test_delete_book(client, auth_headers):
    created = client.post("/books", json=BOOK, headers=auth_headers).json()

    response = client.delete(f"/books/{created['id']}", headers=auth_headers)

    assert response.status_code == 204
    assert client.get(f"/books/{created['id']}").status_code == 404


def test_delete_requires_login(client, auth_headers):
    created = client.post("/books", json=BOOK, headers=auth_headers).json()

    assert client.delete(f"/books/{created['id']}").status_code == 401


def test_delete_unknown_book_returns_404(client, auth_headers):
    assert client.delete("/books/99", headers=auth_headers).status_code == 404
