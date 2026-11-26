from src.domain.entities.catalog_book import CatalogBook
from src.domain.exceptions import CatalogQueryTooShortError
from src.domain.services import BookCatalogProvider


class SearchCatalogUseCase:
    def __init__(self, provider: BookCatalogProvider):
        self.provider = provider

    async def execute(self, query: str, limit: int = 10) -> list[CatalogBook]:
        cleaned = query.strip()
        if len(cleaned) < 2:
            raise CatalogQueryTooShortError()

        return await self.provider.search(cleaned, limit)
