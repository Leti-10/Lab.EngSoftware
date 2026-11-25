from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.social import (
    Comment,
    Follow,
    Notification,
    NotificationPreference,
)
from src.domain.enums.enums import EnumFollowTarget
from src.domain.repositories.social_repository import (
    CommentRepository,
    FollowRepository,
    NotificationPreferenceRepository,
    NotificationRepository,
)
from src.infrastructure.persistence.models.social_model import (
    CommentModelSQLAlchemy,
    FollowModelSQLAlchemy,
    NotificationModelSQLAlchemy,
    NotificationPreferenceModelSQLAlchemy,
)


def _comment(model: CommentModelSQLAlchemy) -> Comment:
    return Comment(
        id=model.id,
        review_id=model.review_id,
        user_id=model.user_id,
        text=model.text,
        created_at=model.created_at,
    )


def _follow(model: FollowModelSQLAlchemy) -> Follow:
    return Follow(
        id=model.id,
        follower_id=model.follower_id,
        target_type=model.target_type,
        target_id=model.target_id,
        created_at=model.created_at,
    )


def _notification(model: NotificationModelSQLAlchemy) -> Notification:
    return Notification(
        id=model.id,
        user_id=model.user_id,
        type=model.type,
        actor_id=model.actor_id,
        review_id=model.review_id,
        book_id=model.book_id,
        read=model.read,
        created_at=model.created_at,
    )


class SQLAlchemyCommentRepository(CommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, comment: Comment) -> Comment:
        model = CommentModelSQLAlchemy(
            review_id=comment.review_id,
            user_id=comment.user_id,
            text=comment.text,
            created_at=comment.created_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _comment(model)

    async def get_by_id(self, comment_id: int) -> Comment | None:
        model = await self.session.get(CommentModelSQLAlchemy, comment_id)
        return _comment(model) if model is not None else None

    async def delete(self, comment_id: int) -> bool:
        model = await self.session.get(CommentModelSQLAlchemy, comment_id)
        if model is None:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def find_by_review(self, review_id: int) -> list[Comment]:
        result = await self.session.execute(
            select(CommentModelSQLAlchemy)
            .where(CommentModelSQLAlchemy.review_id == review_id)
            .order_by(CommentModelSQLAlchemy.id)
        )
        return [_comment(model) for model in result.scalars().all()]


class SQLAlchemyFollowRepository(FollowRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _match(self, follower_id: int, target_type: EnumFollowTarget, target_id: int):
        return (
            FollowModelSQLAlchemy.follower_id == follower_id,
            FollowModelSQLAlchemy.target_type == target_type.value,
            FollowModelSQLAlchemy.target_id == target_id,
        )

    async def save(self, follow: Follow) -> Follow:
        result = await self.session.execute(
            select(FollowModelSQLAlchemy).where(
                *self._match(follow.follower_id, follow.target_type, follow.target_id)
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = FollowModelSQLAlchemy(
                follower_id=follow.follower_id,
                target_type=follow.target_type.value,
                target_id=follow.target_id,
                created_at=follow.created_at,
            )
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
        return _follow(model)

    async def delete(
        self, follower_id: int, target_type: EnumFollowTarget, target_id: int
    ) -> bool:
        result = await self.session.execute(
            delete(FollowModelSQLAlchemy).where(
                *self._match(follower_id, target_type, target_id)
            )
        )
        await self.session.commit()
        return bool(result.rowcount)

    async def exists(
        self, follower_id: int, target_type: EnumFollowTarget, target_id: int
    ) -> bool:
        result = await self.session.execute(
            select(FollowModelSQLAlchemy.id).where(
                *self._match(follower_id, target_type, target_id)
            )
        )
        return result.first() is not None

    async def find_by_follower(
        self, follower_id: int, target_type: EnumFollowTarget | None = None
    ) -> list[Follow]:
        query = select(FollowModelSQLAlchemy).where(
            FollowModelSQLAlchemy.follower_id == follower_id
        )
        if target_type is not None:
            query = query.where(FollowModelSQLAlchemy.target_type == target_type.value)
        result = await self.session.execute(query.order_by(FollowModelSQLAlchemy.id))
        return [_follow(model) for model in result.scalars().all()]

    async def count_followers(
        self, target_type: EnumFollowTarget, target_id: int
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(FollowModelSQLAlchemy)
            .where(
                FollowModelSQLAlchemy.target_type == target_type.value,
                FollowModelSQLAlchemy.target_id == target_id,
            )
        )
        return int(result.scalar_one())


class SQLAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, notification: Notification) -> Notification:
        model = NotificationModelSQLAlchemy(
            user_id=notification.user_id,
            type=notification.type.value,
            actor_id=notification.actor_id,
            review_id=notification.review_id,
            book_id=notification.book_id,
            read=notification.read,
            created_at=notification.created_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _notification(model)

    async def find_by_user(self, user_id: int, limit: int = 50) -> list[Notification]:
        result = await self.session.execute(
            select(NotificationModelSQLAlchemy)
            .where(NotificationModelSQLAlchemy.user_id == user_id)
            .order_by(NotificationModelSQLAlchemy.id.desc())
            .limit(limit)
        )
        return [_notification(model) for model in result.scalars().all()]

    async def count_unread(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(NotificationModelSQLAlchemy)
            .where(
                NotificationModelSQLAlchemy.user_id == user_id,
                NotificationModelSQLAlchemy.read.is_(False),
            )
        )
        return int(result.scalar_one())

    async def mark_read(self, user_id: int, notification_id: int) -> bool:
        result = await self.session.execute(
            update(NotificationModelSQLAlchemy)
            .where(
                NotificationModelSQLAlchemy.id == notification_id,
                NotificationModelSQLAlchemy.user_id == user_id,
            )
            .values(read=True)
        )
        await self.session.commit()
        return bool(result.rowcount)

    async def mark_all_read(self, user_id: int) -> None:
        await self.session.execute(
            update(NotificationModelSQLAlchemy)
            .where(NotificationModelSQLAlchemy.user_id == user_id)
            .values(read=True)
        )
        await self.session.commit()


class SQLAlchemyNotificationPreferenceRepository(NotificationPreferenceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> NotificationPreference:
        model = await self.session.get(NotificationPreferenceModelSQLAlchemy, user_id)
        if model is None:
            return NotificationPreference(user_id=user_id)
        return NotificationPreference(
            user_id=model.user_id,
            likes=model.likes,
            comments=model.comments,
            follows=model.follows,
        )

    async def save(self, preference: NotificationPreference) -> NotificationPreference:
        model = await self.session.get(
            NotificationPreferenceModelSQLAlchemy, preference.user_id
        )
        if model is None:
            model = NotificationPreferenceModelSQLAlchemy(user_id=preference.user_id)
            self.session.add(model)
        model.likes = preference.likes
        model.comments = preference.comments
        model.follows = preference.follows
        await self.session.commit()
        return preference
