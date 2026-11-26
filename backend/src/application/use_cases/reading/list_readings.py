from src.domain.entities import Reading
from src.domain.enums.enums import EnumReadingStatus
from src.domain.repositories import ReadingRepository


class ListReadingsUseCase:
    def __init__(self, reading_repository: ReadingRepository):
        self.reading_repository = reading_repository

    async def execute(
        self,
        user_id: int,
        book_id: int | None = None,
        status: EnumReadingStatus | None = None,
    ) -> list[Reading]:
        return await self.reading_repository.find_by_user(
            user_id, book_id=book_id, status=status
        )
