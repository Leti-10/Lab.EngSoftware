from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.domain.entities import Report
from src.domain.repositories import ReportRepository
from src.infrastructure.persistence.mappers import ReportMapper
from src.infrastructure.persistence.models import ReportModelSQLAlchemy


class SQLAlchemyReportRepository(ReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, report: Report) -> Report:
        model = ReportMapper.to_sqlalchemy(report)
        self.session.add(model)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
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
