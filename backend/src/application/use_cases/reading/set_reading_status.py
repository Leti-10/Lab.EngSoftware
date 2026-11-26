from src.domain.entities import Reading
from src.domain.repositories import ReadingRepository


class SetReadingStatusUseCase:
    def __init__(self, reading_repository: ReadingRepository):
        self.reading_repository = reading_repository

    async def execute(self, reading: Reading) -> Reading:
        return await self.reading_repository.save(reading)
