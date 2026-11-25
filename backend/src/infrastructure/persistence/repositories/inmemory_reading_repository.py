from src.domain.entities import Reading
from src.domain.enums.enums import EnumReadingStatus
from src.domain.repositories import ReadingRepository


class InMemoryReadingRepository(ReadingRepository):
    def __init__(self):
        self.readings: dict[tuple[int, int], Reading] = {}
        self._next_id = 1

    async def save(self, reading: Reading) -> Reading:
        key = (reading.user_id, reading.book_id)
        existing = self.readings.get(key)
        if existing is not None:
            existing.status = reading.status
            return existing
        reading.id = self._next_id
        self._next_id += 1
        self.readings[key] = reading
        return reading

    async def delete(self, user_id: int, book_id: int) -> bool:
        return self.readings.pop((user_id, book_id), None) is not None

    async def find_by_user(
        self,
        user_id: int,
        book_id: int | None = None,
        status: EnumReadingStatus | None = None,
    ) -> list[Reading]:
        return [
            reading
            for reading in self.readings.values()
            if reading.user_id == user_id
            and (book_id is None or reading.book_id == book_id)
            and (status is None or reading.status == status)
        ]
