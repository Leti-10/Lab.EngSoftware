from abc import ABC, abstractmethod
from src.domain.entities import Report


class ReportRepository(ABC):
    @abstractmethod
    async def save(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def get_by_id(self, report_id: int) -> Report | None:
        pass

    @abstractmethod
    async def find_by_filter(
        self,
        description: str | None = None,
        user_name: str | None = None,
        target_type: str | None = None,
        target_name: str | None = None,
    ) -> list[Report | None]:
        pass
