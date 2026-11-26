import pytest

from src.domain.entities.catalog_book import CatalogBook
from src.domain.exceptions import CatalogUnavailableError
from src.domain.services import BookCatalogProvider
from src.presentation.api.main import app
from src.presentation.api.routes.catalog_router import get_catalog_provider


class FakeProvider(BookCatalogProvider):
    def __init__(self, failing=False):
        self.failing = failing
        self.queries: list[str] = []

    async def search(self, query, limit):
        self.queries.append(query)
        if self.failing:
            raise CatalogUnavailableError()
        return [
            CatalogBook(
                isbn="9788532524935",
                title="Jogos Vorazes",
                authors=["Suzanne Collins"],
                publisher="Rocco",
                genres=["Ficção"],
                cover_url="https://covers.openlibrary.org/b/id/1-M.jpg",
            )
        ]


@pytest.fixture
def provider():
    fake = FakeProvider()
    app.dependency_overrides[get_catalog_provider] = lambda: fake
    return fake


def test_search_requires_login(client, provider):
    assert client.get("/catalog/search", params={"q": "jogos"}).status_code == 401


def test_search_returns_normalized_results(client, auth_headers, provider):
    response = client.get(
        "/catalog/search", params={"q": "  jogos vorazes "}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "isbn": "9788532524935",
            "title": "Jogos Vorazes",
            "authors": ["Suzanne Collins"],
            "publisher": "Rocco",
            "genres": ["Ficção"],
            "cover_url": "https://covers.openlibrary.org/b/id/1-M.jpg",
        }
    ]
    assert provider.queries == ["jogos vorazes"]


def test_search_rejects_short_query_without_calling_the_provider(
    client, auth_headers, provider
):
    response = client.get("/catalog/search", params={"q": "a"}, headers=auth_headers)

    assert response.status_code == 422
    assert "ao menos 2 caracteres" in response.json()["detail"]
    assert provider.queries == []


def test_search_without_query_returns_422(client, auth_headers, provider):
    assert client.get("/catalog/search", headers=auth_headers).status_code == 422


def test_search_returns_502_when_the_source_is_down(client, auth_headers):
    app.dependency_overrides[get_catalog_provider] = lambda: FakeProvider(failing=True)

    response = client.get("/catalog/search", params={"q": "dune"}, headers=auth_headers)

    assert response.status_code == 502
    assert "indisponível" in response.json()["detail"]
