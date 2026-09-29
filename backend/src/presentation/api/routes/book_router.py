from fastapi import APIRouter, Depends, status
from src.domain.entities.book import Book
from src.application.use_cases.book import CreateBookUseCase
from src.presentation.api.schemas import CreateBookSchema
from src.infrastructure.persistence.repositories import (
    SQLAlchemyRepository,
    InMemoryBookRepository
)
from src.domain.repositories import BookRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.persistence.database import get_db_context

router = APIRouter(prefix="/books", tags=["Books"])

in_memory_repo_instance = InMemoryBookRepository()

# 2. Cria uma função de fábrica para o Depends consumir
def get_book_m_repository() -> BookRepository:
    return in_memory_repo_instance

async def get_book_repository(
    session: AsyncSession = Depends(get_db_context),
) -> BookRepository:
    return SQLAlchemyRepository(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: CreateBookSchema,
    repository: BookRepository = Depends(get_book_m_repository),
):
    try:
        use_case = CreateBookUseCase(repository)
        novo_book = await use_case.execute(Book(**payload.model_dump()))

        return novo_book
    except Exception as e:
        return e


@router.get("/{book_id}")
async def get_book(book_id: int):
    return {"book_id": book_id}
