from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.domain.entities import Report
from src.domain.exceptions import ReportAlreadyExistsError
from src.domain.repositories import ReportRepository
from src.infrastructure.persistence.mappers import ReportMapper
from src.infrastructure.persistence.models import ReportModelSQLAlchemy


class SQLAlchemyReportRepository(ReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, report: Report) -> Report:
        duplicate_query = select(ReportModelSQLAlchemy.id).where(
            ReportModelSQLAlchemy.user_id == report.user_id,
            ReportModelSQLAlchemy.target_entity == report.target_entity,
            ReportModelSQLAlchemy.target_id == report.target_id,
        )
        if report.id is not None:
            duplicate_query = duplicate_query.where(
                ReportModelSQLAlchemy.id != report.id
            )
        if await self.session.scalar(duplicate_query) is not None:
            raise ReportAlreadyExistsError()

        model = ReportMapper.to_sqlalchemy(report)
        self.session.add(model)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            error = exc.orig
            constraint_name = getattr(error, "constraint_name", None)
            if constraint_name is None:
                constraint_name = getattr(
                    getattr(error, "diag", None),
                    "constraint_name",
                    None,
                )
            if constraint_name == "uq_reports_user_target" or (
                "UNIQUE constraint failed: reports.user_id, "
                "reports.target_entity, reports.target_id"
            ) in str(error):
                raise ReportAlreadyExistsError() from exc
            raise
        await self.session.refresh(model)
        return ReportMapper.to_domain(model)

    async def get_by_id(self, report_id: int) -> Report | None:
        result = await self.session.execute(
            select(ReportModelSQLAlchemy).where(
                ReportModelSQLAlchemy.id == report_id
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return ReportMapper.to_domain(model)

    async def find_by_filter(
        self,
        user_id: int | None = None,
        target_id: int | None = None,
        target_entity: str | None = None,
    ) -> list[Report]:
        query = select(ReportModelSQLAlchemy)
        if user_id is not None:
            query = query.where(ReportModelSQLAlchemy.user_id == user_id)
        if target_id is not None:
            query = query.where(ReportModelSQLAlchemy.target_id == target_id)
        if target_entity:
            query = query.where(
                ReportModelSQLAlchemy.target_entity == target_entity
            )

        result = await self.session.execute(query)
        return [ReportMapper.to_domain(model) for model in result.scalars().all()]
