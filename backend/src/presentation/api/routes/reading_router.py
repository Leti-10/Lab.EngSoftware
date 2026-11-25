from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.reading import (
    ListReadingsUseCase,
    RemoveReadingUseCase,
    SetReadingStatusUseCase,
)
from src.domain.entities import Reading, User
from src.domain.enums.enums import EnumReadingStatus
from src.domain.repositories import ReadingRepository
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import SQLAlchemyReadingRepository
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.schemas.reading_schema import (
    ReadingResponseSchema,
    SetReadingSchema,
)

router = APIRouter(prefix="/readings", tags=["Readings"])


async def get_reading_repository(
    session: AsyncSession = Depends(get_db_context),
) -> ReadingRepository:
    return SQLAlchemyReadingRepository(session)


@router.get("", response_model=list[ReadingResponseSchema])
async def list_my_readings(
    book_id: int | None = Query(default=None, gt=0),
    status_filter: EnumReadingStatus | None = Query(default=None, alias="status"),
    repository: ReadingRepository = Depends(get_reading_repository),
    current_user: User = Depends(get_current_user),
) -> list[ReadingResponseSchema]:
    readings = await ListReadingsUseCase(repository).execute(
        current_user.id, book_id=book_id, status=status_filter
    )
    return [ReadingResponseSchema.model_validate(reading) for reading in readings]


@router.put("/{book_id}")
async def set_reading_status(
    book_id: int,
    payload: SetReadingSchema,
    repository: ReadingRepository = Depends(get_reading_repository),
    current_user: User = Depends(get_current_user),
) -> ReadingResponseSchema:
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="O livro informado é inválido.",
        )
    saved = await SetReadingStatusUseCase(repository).execute(
        Reading(user_id=current_user.id, book_id=book_id, status=payload.status)
    )
    return ReadingResponseSchema.model_validate(saved)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reading(
    book_id: int,
    repository: ReadingRepository = Depends(get_reading_repository),
    current_user: User = Depends(get_current_user),
) -> None:
    removed = await RemoveReadingUseCase(repository).execute(current_user.id, book_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Você não marcou esta obra.",
        )
