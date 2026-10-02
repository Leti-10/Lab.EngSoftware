import pytest

from src.domain.entities.catalog_book import CatalogBook
from src.domain.exceptions import CatalogUnavailableError
from src.domain.services import BookCatalogProvider
from src.infrastructure.catalog import FallbackCatalogProvider
from src.infrastructure.catalog.google_books_provider import parse_google_books
from src.infrastructure.catalog.open_library_provider import parse_open_library, pick_isbn


class Working(BookCatalogProvider):
    def __init__(self):
        self.calls = 0

    async def search(self, query, limit):
        self.calls += 1
        return [CatalogBook(isbn="9788542603835", title=query)]


class Broken(BookCatalogProvider):
    def __init__(self):
        self.calls = 0

    async def search(self, query, limit):
        self.calls += 1
        raise CatalogUnavailableError()


def test_open_library_picks_first_isbn_13():
    assert pick_isbn(["8532530788", "9788532530783", "9781407157863"]) == "9788532530783"
    assert pick_isbn(["8532530788"]) is None


def test_open_library_parser_maps_fields_and_cover():
    payload = {
        "docs": [
            {
                "title": "Dom Casmurro",
                "author_name": ["Machado de Assis"],
                "isbn": ["9788500507007"],
                "publisher": ["Ática", "Outra"],
                "cover_i": 647501,
            }
        ]
    }

    [book] = parse_open_library(payload, limit=10)

    assert book.isbn == "9788500507007"
    assert book.title == "Dom Casmurro"
    assert book.authors == ["Machado de Assis"]
    assert book.publisher == "Ática"
    assert book.cover_url == "https://covers.openlibrary.org/b/id/647501-M.jpg"


def test_open_library_parser_skips_docs_without_isbn_or_title_and_duplicates():
    payload = {
        "docs": [
            {"title": "Sem ISBN", "isbn": ["123"]},
            {"title": "", "isbn": ["9788500507007"]},
            {"title": "Livro", "isbn": ["9788500507007"]},
            {"title": "Livro repetido", "isbn": ["9788500507007"]},
        ]
    }

    results = parse_open_library(payload, limit=10)

    assert [book.title for book in results] == ["Livro"]


def test_open_library_parser_respects_limit_and_handles_missing_optional_fields():
    payload = {"docs": [{"title": f"Livro {i}", "isbn": [f"97885005070{i:02d}"]} for i in range(5)]}

    results = parse_open_library(payload, limit=2)

    assert len(results) == 2
    assert results[0].authors == []
    assert results[0].publisher == ""
    assert results[0].cover_url is None


def test_google_books_parser_prefers_isbn_13_and_secures_cover():
    payload = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Jogos Vorazes",
                    "authors": ["Suzanne Collins"],
                    "publisher": "Rocco",
                    "categories": ["Fiction"],
                    "industryIdentifiers": [
                        {"type": "ISBN_10", "identifier": "8532524931"},
                        {"type": "ISBN_13", "identifier": "9788532524935"},
                    ],
                    "imageLinks": {"thumbnail": "http://books.google.com/cover.jpg"},
                }
            }
        ]
    }

    [book] = parse_google_books(payload, limit=10)

    assert book.isbn == "9788532524935"
    assert book.genres == ["Fiction"]
    assert book.cover_url == "https://books.google.com/cover.jpg"


def test_google_books_parser_falls_back_to_isbn_10_and_skips_without_isbn():
    payload = {
        "items": [
            {"volumeInfo": {"title": "Sem ISBN"}},
            {
                "volumeInfo": {
                    "title": "Só ISBN 10",
                    "industryIdentifiers": [{"type": "ISBN_10", "identifier": "8532524931"}],
                }
            },
        ]
    }

    results = parse_google_books(payload, limit=10)

    assert [book.isbn for book in results] == ["8532524931"]


async def test_fallback_uses_the_first_working_provider():
    first, second = Working(), Working()

    results = await FallbackCatalogProvider([first, second]).search("dune", 5)

    assert results[0].title == "dune"
    assert (first.calls, second.calls) == (1, 0)


async def test_fallback_moves_to_the_next_provider_when_one_fails():
    broken, working = Broken(), Working()

    results = await FallbackCatalogProvider([broken, working]).search("dune", 5)

    assert results[0].title == "dune"
    assert (broken.calls, working.calls) == (1, 1)


async def test_fallback_raises_when_every_provider_fails():
    with pytest.raises(CatalogUnavailableError):
        await FallbackCatalogProvider([Broken(), Broken()]).search("dune", 5)
