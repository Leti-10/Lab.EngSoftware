from src.domain.entities import Report
from src.domain.repositories import ReportRepository


class GetReportByIdUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def execute(self, report_id: int) -> Report | None:
        return await self.report_repository.get_by_id(report_id)
