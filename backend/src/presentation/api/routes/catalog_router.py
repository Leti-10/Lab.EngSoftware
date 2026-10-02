from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases import SearchCatalogUseCase
from src.core.config import settings
from src.domain.entities import User
from src.domain.exceptions import CatalogQueryTooShortError, CatalogUnavailableError
from src.domain.services import BookCatalogProvider
from src.infrastructure.catalog import (
    FallbackCatalogProvider,
    GoogleBooksProvider,
    OpenLibraryProvider,
)
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.schemas.catalog_schema import CatalogBookSchema

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@lru_cache
def get_catalog_provider() -> BookCatalogProvider:
    timeout = settings.CATALOG_TIMEOUT_SECONDS
    providers: list[BookCatalogProvider] = []
    if settings.GOOGLE_BOOKS_API_KEY:
        providers.append(GoogleBooksProvider(settings.GOOGLE_BOOKS_API_KEY, timeout))
    providers.append(OpenLibraryProvider(timeout))
    return FallbackCatalogProvider(providers)


@router.get("/search")
async def search_catalog(
    q: str = "",
    provider: BookCatalogProvider = Depends(get_catalog_provider),
    _current_user: User = Depends(get_current_user),
) -> list[CatalogBookSchema]:
    try:
        results = await SearchCatalogUseCase(provider).execute(q)
    except CatalogQueryTooShortError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.message
        ) from error
    except CatalogUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=error.message
        ) from error

    return [
        CatalogBookSchema(
            isbn=book.isbn,
            title=book.title,
            authors=book.authors,
            publisher=book.publisher,
            genres=book.genres,
            cover_url=book.cover_url,
        )
        for book in results
    ]
