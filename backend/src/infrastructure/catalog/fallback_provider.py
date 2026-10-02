from src.domain.entities.catalog_book import CatalogBook
from src.domain.exceptions import CatalogUnavailableError
from src.domain.services import BookCatalogProvider


class FallbackCatalogProvider(BookCatalogProvider):
    def __init__(self, providers: list[BookCatalogProvider]):
        self.providers = providers

    async def search(self, query: str, limit: int) -> list[CatalogBook]:
        for provider in self.providers:
            try:
                return await provider.search(query, limit)
            except CatalogUnavailableError:
                continue
        raise CatalogUnavailableError()
