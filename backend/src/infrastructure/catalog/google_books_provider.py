import urllib.parse

from src.domain.entities.catalog_book import CatalogBook
from src.domain.services import BookCatalogProvider
from src.infrastructure.catalog.http import fetch_json

VOLUMES_URL = "https://www.googleapis.com/books/v1/volumes"


def pick_isbn(identifiers: list[dict]) -> str | None:
    by_type = {item.get("type"): item.get("identifier") for item in identifiers}
    return by_type.get("ISBN_13") or by_type.get("ISBN_10")


def parse_google_books(payload: dict, limit: int) -> list[CatalogBook]:
    results: list[CatalogBook] = []
    seen: set[str] = set()

    for item in payload.get("items", []):
        info = item.get("volumeInfo", {})
        isbn = pick_isbn(info.get("industryIdentifiers", []))
        title = (info.get("title") or "").strip()
        if not isbn or not title or isbn in seen:
            continue

        seen.add(isbn)
        thumbnail = (info.get("imageLinks") or {}).get("thumbnail")
        results.append(
            CatalogBook(
                isbn=isbn,
                title=title,
                authors=list(info.get("authors") or []),
                publisher=info.get("publisher") or "",
                genres=list(info.get("categories") or []),
                cover_url=thumbnail.replace("http://", "https://")
                if thumbnail
                else None,
            )
        )
        if len(results) == limit:
            break

    return results


class GoogleBooksProvider(BookCatalogProvider):
    def __init__(self, api_key: str, timeout: float = 8.0):
        self.api_key = api_key
        self.timeout = timeout

    async def search(self, query: str, limit: int) -> list[CatalogBook]:
        params = urllib.parse.urlencode(
            {
                "q": query,
                "maxResults": min(limit * 2, 40),
                "printType": "books",
                "key": self.api_key,
            }
        )
        payload = await fetch_json(f"{VOLUMES_URL}?{params}", self.timeout)
        return parse_google_books(payload, limit)
