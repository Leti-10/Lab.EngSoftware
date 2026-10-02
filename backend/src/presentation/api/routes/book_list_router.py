from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases import (
    AddBookToListUseCase,
    CreateBookListUseCase,
    GetBookListUseCase,
)
from src.domain.entities import BookList, User
from src.domain.exceptions import (
    BookAlreadyInListError,
    BookListForbiddenError,
    BookListNotFoundError,
    BookNotFoundError,
    DomainError,
)
from src.domain.repositories import BookListRepository, BookRepository
from src.infrastructure.persistence.repositories import InMemoryBookListRepository
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.routes.book_router import get_book_m_repository, to_response
from src.presentation.api.schemas import (
    AddBookToListSchema,
    BookListResponseSchema,
    CreateBookListSchema,
)

router = APIRouter(prefix="/lists", tags=["Lists"])

_book_list_repository = InMemoryBookListRepository()


def get_book_list_repository() -> BookListRepository:
    return _book_list_repository


async def _to_response(
    book_list: BookList, book_repository: BookRepository
) -> BookListResponseSchema:
    books = [await book_repository.get_by_id(book_id) for book_id in book_list.books]
    return BookListResponseSchema(
        id=book_list.id,
        owner=book_list.owner,
        name=book_list.name,
        description=book_list.description,
        private=book_list.private,
        books=[to_response(book) for book in books if book is not None],
    )


def _http_error(error: DomainError) -> HTTPException:
    codes = {
        BookListNotFoundError: status.HTTP_404_NOT_FOUND,
        BookNotFoundError: status.HTTP_404_NOT_FOUND,
        BookListForbiddenError: status.HTTP_403_FORBIDDEN,
        BookAlreadyInListError: status.HTTP_409_CONFLICT,
    }
    return HTTPException(
        status_code=codes.get(type(error), status.HTTP_422_UNPROCESSABLE_CONTENT),
        detail=error.message,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_list(
    payload: CreateBookListSchema,
    current_user: User = Depends(get_current_user),
    repository: BookListRepository = Depends(get_book_list_repository),
    book_repository: BookRepository = Depends(get_book_m_repository),
) -> BookListResponseSchema:
    try:
        new_list = BookList(
            owner=current_user.id,
            name=payload.name.strip(),
            description=payload.description.strip(),
            private=payload.private,
        )
        created = CreateBookListUseCase(repository).execute(new_list)
    except DomainError as error:
        raise _http_error(error) from error
    except ValueError as error:
        conflict = str(error) == "Nome da lista já cadastrado"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if conflict
            else status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return await _to_response(created, book_repository)


@router.get("")
async def my_lists(
    current_user: User = Depends(get_current_user),
    repository: BookListRepository = Depends(get_book_list_repository),
    book_repository: BookRepository = Depends(get_book_m_repository),
) -> list[BookListResponseSchema]:
    lists = repository.list_by_owner(current_user.id)
    return [await _to_response(book_list, book_repository) for book_list in lists]


@router.get("/{list_id}")
async def get_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    repository: BookListRepository = Depends(get_book_list_repository),
    book_repository: BookRepository = Depends(get_book_m_repository),
) -> BookListResponseSchema:
    try:
        book_list = GetBookListUseCase(repository).execute(list_id, current_user.id)
    except DomainError as error:
        raise _http_error(error) from error
    return await _to_response(book_list, book_repository)


@router.post("/{list_id}/books")
async def add_book(
    list_id: int,
    payload: AddBookToListSchema,
    current_user: User = Depends(get_current_user),
    repository: BookListRepository = Depends(get_book_list_repository),
    book_repository: BookRepository = Depends(get_book_m_repository),
) -> BookListResponseSchema:
    try:
        book_list = await AddBookToListUseCase(repository, book_repository).execute(
            list_id, payload.book_id, current_user.id
        )
    except DomainError as error:
        raise _http_error(error) from error
    return await _to_response(book_list, book_repository)
