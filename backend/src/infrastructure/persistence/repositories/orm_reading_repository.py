from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Reading
from src.domain.enums.enums import EnumReadingStatus
from src.domain.repositories import ReadingRepository
from src.infrastructure.persistence.mappers import ReadingMapper
from src.infrastructure.persistence.models import ReadingModelSQLAlchemy


class SQLAlchemyReadingRepository(ReadingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _find_model(
        self, user_id: int, book_id: int
    ) -> ReadingModelSQLAlchemy | None:
        result = await self.session.execute(
            select(ReadingModelSQLAlchemy).where(
                ReadingModelSQLAlchemy.user_id == user_id,
                ReadingModelSQLAlchemy.book_id == book_id,
            )
        )
        return result.scalar_one_or_none()

    async def save(self, reading: Reading) -> Reading:
        model = await self._find_model(reading.user_id, reading.book_id)
        if model is None:
            model = ReadingMapper.to_sqlalchemy(reading)
            self.session.add(model)
        else:
            model.status = reading.status.value
        await self.session.commit()
        await self.session.refresh(model)
        return ReadingMapper.to_domain(model)

    async def delete(self, user_id: int, book_id: int) -> bool:
        model = await self._find_model(user_id, book_id)
        if model is None:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def find_by_user(
        self,
        user_id: int,
        book_id: int | None = None,
        status: EnumReadingStatus | None = None,
    ) -> list[Reading]:
        query = select(ReadingModelSQLAlchemy).where(
            ReadingModelSQLAlchemy.user_id == user_id
        )
        if book_id is not None:
            query = query.where(ReadingModelSQLAlchemy.book_id == book_id)
        if status is not None:
            query = query.where(ReadingModelSQLAlchemy.status == status.value)
        result = await self.session.execute(query.order_by(ReadingModelSQLAlchemy.id))
        return [ReadingMapper.to_domain(model) for model in result.scalars().all()]
