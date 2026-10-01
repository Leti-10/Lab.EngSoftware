from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Vote
from src.domain.repositories import VoteRepository
from src.infrastructure.persistence.mappers import VoteMapper
from src.infrastructure.persistence.models import VoteModelSQLAlchemy


class SQLAlchemyVoteRepository(VoteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, vote: Vote) -> Vote:
        model = VoteMapper.to_sqlalchemy(vote)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return VoteMapper.to_domain(model)

    async def get_by_id(self, vote_id: int) -> Vote | None:
        result = await self.session.execute(
            select(VoteModelSQLAlchemy).where(VoteModelSQLAlchemy.id == vote_id)
        )
        model = result.scalar_one_or_none()
        return VoteMapper.to_domain(model)

    async def find_by_filter(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: str | None = None,
        target_name: str | None = None,
    ) -> list[Vote]:
        raise NotImplementedError("Os filtros de vote dependem das modelagens relacionadas.")