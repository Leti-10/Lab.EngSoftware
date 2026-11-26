from abc import ABC, abstractmethod

from src.domain.entities import Reading
from src.domain.enums.enums import EnumReadingStatus


class ReadingRepository(ABC):
    @abstractmethod
    async def save(self, reading: Reading) -> Reading:
        pass

    @abstractmethod
    async def delete(self, user_id: int, book_id: int) -> bool:
        pass

    @abstractmethod
    async def find_by_user(
        self,
        user_id: int,
        book_id: int | None = None,
        status: EnumReadingStatus | None = None,
    ) -> list[Reading]:
        pass
