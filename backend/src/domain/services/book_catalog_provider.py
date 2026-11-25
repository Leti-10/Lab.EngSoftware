from abc import ABC, abstractmethod

from src.domain.entities.catalog_book import CatalogBook


class BookCatalogProvider(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int) -> list[CatalogBook]:
        pass
