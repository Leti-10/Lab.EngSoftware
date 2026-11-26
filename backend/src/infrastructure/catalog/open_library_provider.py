import urllib.parse

from src.domain.entities.catalog_book import CatalogBook
from src.domain.services import BookCatalogProvider
from src.infrastructure.catalog.http import fetch_json

SEARCH_URL = "https://openlibrary.org/search.json"
FIELDS = "title,author_name,isbn,publisher,cover_i"


def pick_isbn(isbns: list[str]) -> str | None:
    thirteen = [isbn for isbn in isbns if len(isbn) == 13 and isbn.isdigit()]
    return thirteen[0] if thirteen else None


def parse_open_library(payload: dict, limit: int) -> list[CatalogBook]:
    results: list[CatalogBook] = []
    seen: set[str] = set()

    for doc in payload.get("docs", []):
        isbn = pick_isbn(doc.get("isbn", []))
        title = (doc.get("title") or "").strip()
        if not isbn or not title or isbn in seen:
            continue

        seen.add(isbn)
        cover_id = doc.get("cover_i")
        publishers = doc.get("publisher") or [""]
        results.append(
            CatalogBook(
                isbn=isbn,
                title=title,
                authors=list(doc.get("author_name") or []),
                publisher=publishers[0],
                cover_url=(
                    f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                    if cover_id
                    else None
                ),
            )
        )
        if len(results) == limit:
            break

    return results


class OpenLibraryProvider(BookCatalogProvider):
    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout

    async def search(self, query: str, limit: int) -> list[CatalogBook]:
        params = urllib.parse.urlencode(
            {"q": query, "limit": limit * 3, "fields": FIELDS}
        )
        payload = await fetch_json(f"{SEARCH_URL}?{params}", self.timeout)
        return parse_open_library(payload, limit)
