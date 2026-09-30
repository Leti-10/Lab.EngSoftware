from src.domain.entities.report import Report
from src.domain.repositories.report_repository import ReportRepository


class InMemoryReportRepository(ReportRepository):
    def __init__(self):
        self.reports = []

    def save(self, report: Report) -> Report:
        self.reports.append(report)
        return report

    def get_by_id(self, report_id: int) -> Report | None:
        for report in self.reports:
            if report.id == report_id:
                return report
        return None

    async def find_by_filter(
        self,
        description: str | None = None,
        user_name: str | None = None,
        target_type: str | None = None,
        target_name: str | None = None,
    ) -> list[Report | None]:
        results = []
        # TO DO: Esta endpoint será implementada
        # assim que todas as entidades forem criadas

        '''
            for _, report in self.reports.items():
                if description and description not in report.description:
                    continue
                if user_name and user_name not in report.user_name:
                    continue
                if target_type and target_type not in report.target_type:
                    continue
                if target_name and target_name not in report.target_name:
                    continue
                results.append(report)
        
        '''
        return results
    