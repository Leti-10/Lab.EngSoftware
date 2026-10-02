import pytest

from src.application.use_cases import SearchCatalogUseCase
from src.domain.entities.catalog_book import CatalogBook
from src.domain.exceptions import CatalogQueryTooShortError
from src.domain.services import BookCatalogProvider


class Recorder(BookCatalogProvider):
    def __init__(self):
        self.calls: list[tuple[str, int]] = []

    async def search(self, query, limit):
        self.calls.append((query, limit))
        return [CatalogBook(isbn="9788542603835", title="One Piece")]


async def test_should_trim_the_query_before_searching():
    provider = Recorder()

    results = await SearchCatalogUseCase(provider).execute("  one piece  ", limit=5)

    assert provider.calls == [("one piece", 5)]
    assert results[0].title == "One Piece"


@pytest.mark.parametrize("query", ["", " ", "a", "  b "])
async def test_should_reject_queries_shorter_than_two_characters(query):
    provider = Recorder()

    with pytest.raises(CatalogQueryTooShortError):
        await SearchCatalogUseCase(provider).execute(query)

    assert provider.calls == []
