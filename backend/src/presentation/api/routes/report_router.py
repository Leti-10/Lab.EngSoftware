from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from src.application.use_cases.report import (
    CreateReportUseCase,
    FilterReportsUseCase,
    GetReportByIdUseCase,
)
from src.domain.entities import Report, User
from src.domain.repositories import ReportRepository
from src.infrastructure.persistence.repositories import InMemoryReportRepository
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.schemas.report_schema import (
    CreateReportSchema,
    ReportResponseSchema,
)

router = APIRouter(prefix="/reports", tags=["Reports"])

_report_repository = InMemoryReportRepository()


def get_report_repository() -> ReportRepository:
    return _report_repository


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: CreateReportSchema,
    current_user: User = Depends(get_current_user),
    repository: ReportRepository = Depends(get_report_repository),
) -> ReportResponseSchema:
    try:
        created = await CreateReportUseCase(repository).execute(
            Report(user_id=current_user.id, **payload.model_dump())
        )
        return ReportResponseSchema.model_validate(created)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Não foi possível registrar a denúncia.",
        ) from exc


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    _current_user: User = Depends(get_current_user),
    repository: ReportRepository = Depends(get_report_repository),
) -> ReportResponseSchema:
    report = await GetReportByIdUseCase(repository).execute(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Denúncia não encontrada."
        )
    return ReportResponseSchema.model_validate(report)


@router.get("", response_model=list[ReportResponseSchema])
async def filter_reports(
    user_id: int | None = Query(default=None, gt=0),
    target_id: int | None = Query(default=None, gt=0),
    target_entity: str | None = Query(default=None, min_length=1, max_length=50),
    _current_user: User = Depends(get_current_user),
    repository: ReportRepository = Depends(get_report_repository),
) -> list[ReportResponseSchema]:
    reports = await FilterReportsUseCase(repository).execute(
        user_id=user_id,
        target_id=target_id,
        target_entity=target_entity,
    )
    return [ReportResponseSchema.model_validate(report) for report in reports]
