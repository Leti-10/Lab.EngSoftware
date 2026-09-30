from fastapi import APIRouter, Depends, status
from src.domain.entities.report import Report
from src.application.use_cases.report import CreateReportUseCase
from src.presentation.api.schemas import CreateReportSchema
from src.infrastructure.persistence.repositories import (
    SQLAlchemyRepository,
    InMemoryReportRepository
)
from src.domain.repositories import ReportRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.persistence.database import get_db_context

router = APIRouter(prefix="/reports", tags=["Reports"])

in_memory_repo_instance = InMemoryReportRepository()

# 2. Cria uma função de fábrica para o Depends consumir
def get_report_m_repository() -> ReportRepository:
    return in_memory_repo_instance

async def get_report_repository(
    session: AsyncSession = Depends(get_db_context),
) -> ReportRepository:
    return SQLAlchemyRepository(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: CreateReportSchema,
    repository: ReportRepository = Depends(get_report_m_repository),
):
    try:
        use_case = CreateReportUseCase(repository)
        novo_book = await use_case.execute(Report(**payload.model_dump()))

        return novo_book
    except Exception as e:
        return e


@router.get("/{report_id}")
async def get_book(report_id: int):
    return {"report_id": report_id}
