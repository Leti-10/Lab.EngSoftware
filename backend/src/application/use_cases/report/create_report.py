from src.domain.entities import Report
from src.domain.repositories import ReportRepository


class CreateReportUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def execute(self, new_report: Report) -> Report:
        if new_report is None:
            raise ValueError("A denúncia não pode ser nula")

        return await self.report_repository.save(new_report)
