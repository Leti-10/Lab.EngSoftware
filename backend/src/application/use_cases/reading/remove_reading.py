from src.domain.repositories import ReadingRepository


class RemoveReadingUseCase:
    def __init__(self, reading_repository: ReadingRepository):
        self.reading_repository = reading_repository

    async def execute(self, user_id: int, book_id: int) -> bool:
        return await self.reading_repository.delete(user_id, book_id)
