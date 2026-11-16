from src.domain.entities import Report
from src.domain.exceptions import ReportAlreadyExistsError
from src.domain.repositories import ReportRepository


class CreateReportUseCase:
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def execute(self, new_report: Report) -> Report:
        if new_report is None:
            raise ValueError("A denúncia não pode ser nula")

        existing_reports = await self.report_repository.find_by_filter(
            user_id=new_report.user_id,
            target_id=new_report.target_id,
            target_entity=new_report.target_entity,
        )
        if any(report.id != new_report.id for report in existing_reports):
            raise ReportAlreadyExistsError()

        return await self.report_repository.save(new_report)
