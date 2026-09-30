from src.domain.entities import Report
from src.domain.repositories import ReportRepository


class CreateReportUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def execute(self, new_report: Report):
        if new_report is None:
            raise ValueError("O report não pode ser nulo")

        return await self.report_repository.save(new_report)
