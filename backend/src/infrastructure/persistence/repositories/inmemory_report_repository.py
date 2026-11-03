from src.domain.entities import Report
from src.domain.repositories import ReportRepository


class InMemoryReportRepository(ReportRepository):
    def __init__(self):
        self.reports: dict[int, Report] = {}
        self._next_id = 1

    async def save(self, report: Report) -> Report:
        if report.id is None:
            report.id = self._next_id
            self._next_id += 1
        self.reports[report.id] = report
        return report

    async def get_by_id(self, report_id: int) -> Report | None:
        return self.reports.get(report_id)

    async def find_by_filter(
        self,
        user_id: int | None = None,
        target_id: int | None = None,
        target_entity: str | None = None,
    ) -> list[Report]:
        return [
            report
            for report in self.reports.values()
            if (user_id is None or report.user_id == user_id)
            and (target_id is None or report.target_id == target_id)
            and (target_entity is None or report.target_entity == target_entity)
        ]
