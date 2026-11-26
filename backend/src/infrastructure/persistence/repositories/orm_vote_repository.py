from collections.abc import Sequence

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Vote
from src.domain.enums.enums import EnumVoteTarget
from src.domain.exceptions import VoteAlreadyExistsError
from src.domain.repositories import BookListRepository, VoteRepository
from src.infrastructure.persistence.mappers import VoteMapper
from src.infrastructure.persistence.models.book_model import BookModelSQLAlchemy
from src.infrastructure.persistence.models.review_model import ReviewModelSQLAlchemy
from src.infrastructure.persistence.models.user_model import UserModelSQLAlchemy
from src.infrastructure.persistence.models.vote_model import VoteModelSQLAlchemy
from src.infrastructure.telemetry import logger_decorator


class SQLAlchemyVoteRepository(VoteRepository):
    def __init__(
        self,
        session: AsyncSession,
        book_list_repository: BookListRepository | None = None,
    ):
        self.session = session
        self.book_list_repository = book_list_repository

    @logger_decorator
    async def save(self, vote: Vote) -> Vote:
        duplicate_query = select(VoteModelSQLAlchemy.id).where(
            VoteModelSQLAlchemy.user_id == vote.user_id,
            VoteModelSQLAlchemy.target_entity == vote.target_entity.value,
            VoteModelSQLAlchemy.target_id == vote.target_id,
        )
        if vote.id is not None:
            duplicate_query = duplicate_query.where(VoteModelSQLAlchemy.id != vote.id)
        if await self.session.scalar(duplicate_query) is not None:
            raise VoteAlreadyExistsError()

        if vote.id is not None:
            existing_model = await self.session.get(VoteModelSQLAlchemy, vote.id)
            if existing_model is not None:
                existing_model.status = vote.status
                existing_model.target_entity = vote.target_entity.value
                existing_model.target_id = vote.target_id
                existing_model.user_id = vote.user_id
                await self.session.commit()
                await self.session.refresh(existing_model)
                return VoteMapper.to_domain(existing_model)

        model = VoteMapper.to_sqlalchemy(vote)
        self.session.add(model)
        try:
            await self.session.commit()
            await self.session.refresh(model)
        except IntegrityError as exc:
            await self.session.rollback()
            error = exc.orig
            constraint_name = getattr(error, "constraint_name", None)
            if constraint_name == "uq_votes_user_target" or (
                "UNIQUE constraint failed: votes.user_id, "
                "votes.target_entity, votes.target_id"
            ) in str(error):
                raise VoteAlreadyExistsError() from exc
            raise
        return VoteMapper.to_domain(model)

    @logger_decorator
    async def get_by_id(self, vote_id: int) -> Vote | None:
        result = await self.session.execute(
            select(VoteModelSQLAlchemy).where(VoteModelSQLAlchemy.id == vote_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return VoteMapper.to_domain(model)

    @logger_decorator
    async def delete(self, vote_id: int) -> bool:
        model = await self.session.get(VoteModelSQLAlchemy, vote_id)
        if model is None:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True

    @logger_decorator
    async def delete_by_target(
        self,
        user_id: int,
        target_type: EnumVoteTarget,
        target_id: int,
        status: str,
    ) -> bool:
        result = await self.session.execute(
            delete(VoteModelSQLAlchemy).where(
                VoteModelSQLAlchemy.user_id == user_id,
                VoteModelSQLAlchemy.target_entity == target_type.value,
                VoteModelSQLAlchemy.target_id == target_id,
                VoteModelSQLAlchemy.status == status,
            )
        )
        await self.session.commit()
        return bool(result.rowcount)

    @logger_decorator
    async def find_by_filter(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: EnumVoteTarget | None = None,
        target_name: str | None = None,
        user_id: int | None = None,
        target_ids: Sequence[int] | None = None,
    ) -> list[Vote]:
        query = select(VoteModelSQLAlchemy)
        if user_id is not None:
            query = query.where(VoteModelSQLAlchemy.user_id == user_id)
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
            query = query.where(VoteModelSQLAlchemy.target_entity == target_type.value)
        if target_ids is not None:
            query = query.where(VoteModelSQLAlchemy.target_id.in_(target_ids))
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
                    book_list = await self.book_list_repository.get_by_name(target_name)
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
