from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.book import (
    CreateBookUseCase,
    DeleteBookUseCase,
    GetBookUseCase,
    SearchBooksUseCase,
    UpdateBookUseCase,
)
from src.domain.entities import User
from src.domain.entities.book import Book
from src.domain.exceptions import BookNotFoundError
from src.domain.repositories import BookRepository
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import (
    InMemoryBookRepository,
    SQLAlchemyRepository,
)
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.schemas import BookResponseSchema, CreateBookSchema

router = APIRouter(prefix="/books", tags=["Books"])

in_memory_repo_instance = InMemoryBookRepository()


def get_book_m_repository() -> BookRepository:
    return in_memory_repo_instance


async def get_book_repository(
    session: AsyncSession = Depends(get_db_context),
) -> BookRepository:
    return SQLAlchemyRepository(session)


def to_response(book: Book) -> BookResponseSchema:
    authors = [book.authors] if isinstance(book.authors, str) else list(book.authors)
    return BookResponseSchema(
        id=book.id,
        isbn=book.isbn,
        title=book.title,
        publisher=book.publisher,
        authors=authors,
        genre=list(book.genre),
        theme=list(book.theme),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: CreateBookSchema,
    repository: BookRepository = Depends(get_book_m_repository),
    _current_user: User = Depends(get_current_user),
) -> BookResponseSchema:
    try:
        book = Book(**payload.model_dump())
        created = await CreateBookUseCase(repository).execute(book)
    except ValueError as error:
        conflict = str(error) == "ISBN já cadastrado"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if conflict
            else status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return to_response(created)


@router.get("")
async def list_books(
    q: str | None = None,
    genre: str | None = None,
    repository: BookRepository = Depends(get_book_m_repository),
) -> list[BookResponseSchema]:
    books = await SearchBooksUseCase(repository).execute(query=q, genre=genre)
    return [to_response(book) for book in books]


@router.get("/{book_id}")
async def get_book(
    book_id: int,
    repository: BookRepository = Depends(get_book_m_repository),
) -> BookResponseSchema:
    try:
        book = await GetBookUseCase(repository).execute(book_id)
    except BookNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error
    return to_response(book)


@router.put("/{book_id}")
async def update_book(
    book_id: int,
    payload: CreateBookSchema,
    repository: BookRepository = Depends(get_book_m_repository),
    _current_user: User = Depends(get_current_user),
) -> BookResponseSchema:
    try:
        updated = await UpdateBookUseCase(repository).execute(
            book_id, Book(**payload.model_dump())
        )
    except BookNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error
    except ValueError as error:
        conflict = str(error) == "ISBN já cadastrado"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if conflict
            else status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return to_response(updated)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    repository: BookRepository = Depends(get_book_m_repository),
    _current_user: User = Depends(get_current_user),
) -> None:
    try:
        await DeleteBookUseCase(repository).execute(book_id)
    except BookNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error
