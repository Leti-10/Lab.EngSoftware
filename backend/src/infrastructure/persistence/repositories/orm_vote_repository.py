from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Vote
from src.domain.enums.enums import EnumVoteTarget
from src.domain.repositories import BookListRepository, VoteRepository
from src.infrastructure.persistence.mappers import VoteMapper
from src.infrastructure.persistence.models.book_model import BookModelSQLAlchemy
from src.infrastructure.persistence.models.review_model import ReviewModelSQLAlchemy
from src.infrastructure.persistence.models.user_model import UserModelSQLAlchemy
from src.infrastructure.persistence.models.vote_model import VoteModelSQLAlchemy


class SQLAlchemyVoteRepository(VoteRepository):
    def __init__(
        self,
        session: AsyncSession,
        book_list_repository: BookListRepository | None = None,
    ):
        self.session = session
        self.book_list_repository = book_list_repository

    async def save(self, vote: Vote) -> Vote:
        model = VoteMapper.to_sqlalchemy(vote)
        self.session.add(model)
        try:
            await self.session.commit()
            await self.session.refresh(model)
        except IntegrityError:
            await self.session.rollback()
            raise
        return VoteMapper.to_domain(model)

    async def get_by_id(self, vote_id: int) -> Vote | None:
        result = await self.session.execute(
            select(VoteModelSQLAlchemy).where(VoteModelSQLAlchemy.id == vote_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return VoteMapper.to_domain(model)

    async def delete(self, vote_id: int) -> bool:
        model = await self.session.get(VoteModelSQLAlchemy, vote_id)
        if model is None:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True

    async def find_by_filter(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: EnumVoteTarget | None = None,
        target_name: str | None = None,
    ) -> list[Vote]:
        query = select(VoteModelSQLAlchemy)
        if status is not None:
            query = query.where(VoteModelSQLAlchemy.status == status)
        if user_name:
            query = query.where(
                VoteModelSQLAlchemy.user_id.in_(
                    select(UserModelSQLAlchemy.id).where(
                        UserModelSQLAlchemy.username.ilike(f"%{user_name}%")
                    )
                )
            )
        if target_type is not None:
            query = query.where(
                VoteModelSQLAlchemy.target_entity == target_type.value
            )
        if target_name:
            pattern = f"%{target_name}%"
            target_filters = []
            target_types = (
                [target_type] if target_type is not None else list(EnumVoteTarget)
            )

            for current_type in target_types:
                if current_type == EnumVoteTarget.BOOK:
                    target_ids = select(BookModelSQLAlchemy.id).where(
                        BookModelSQLAlchemy.title.ilike(pattern)
                    )
                elif current_type == EnumVoteTarget.REVIEW:
                    target_ids = select(ReviewModelSQLAlchemy.id).where(
                        ReviewModelSQLAlchemy.comment.ilike(pattern)
                    )
                elif current_type == EnumVoteTarget.LIST:
                    if self.book_list_repository is None:
                        raise ValueError(
                            "A busca pelo nome de listas exige um "
                            "repositório de listas."
                        )
                    book_list = self.book_list_repository.get_by_name(target_name)
                    target_ids = [book_list.id] if book_list is not None else []
                else:
                    continue

                target_filters.append(
                    and_(
                        VoteModelSQLAlchemy.target_entity == current_type.value,
                        VoteModelSQLAlchemy.target_id.in_(target_ids),
                    )
                )

            query = query.where(or_(*target_filters))

        result = await self.session.execute(query)
        return [VoteMapper.to_domain(model) for model in result.scalars().all()]