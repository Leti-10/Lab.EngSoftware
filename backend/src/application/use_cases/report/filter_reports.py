from src.domain.entities import Report
from src.domain.repositories import ReportRepository


class FilterReportsUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def execute(
        self,
        user_id: int | None = None,
        target_id: int | None = None,
        target_entity: str | None = None,
    ) -> list[Report]:
        return await self.report_repository.find_by_filter(
            user_id=user_id,
            target_id=target_id,
            target_entity=target_entity,
        )
