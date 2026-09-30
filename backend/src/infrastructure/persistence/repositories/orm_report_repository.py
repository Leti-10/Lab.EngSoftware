from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        await self.session.commit()
        await self.session.refresh(model)
        return ReportMapper.to_domain(model)

    async def get_by_id(self, report_id: int) -> Report | None:
        result = await self.session.execute(
            select(ReportModelSQLAlchemy).where(
                ReportModelSQLAlchemy.id == report_id
            )
        )
        model = result.scalar_one_or_none()
        return ReportMapper.to_domain(model)

    async def find_by_filter(
        self,
        description: str | None = None,
        user_name: str | None = None,
        target_type: str | None = None,
        target_name: str | None = None,
    ) -> list[Report | None]:
        raise NotImplementedError(
            "O filtro de reports será implementado após as modelagens relacionadas."
        )