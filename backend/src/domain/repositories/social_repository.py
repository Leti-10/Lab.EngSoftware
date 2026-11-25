from abc import ABC, abstractmethod

from src.domain.entities.social import (
    Comment,
    Follow,
    Notification,
    NotificationPreference,
)
from src.domain.enums.enums import EnumFollowTarget


class CommentRepository(ABC):
    @abstractmethod
    async def save(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Comment | None:
        pass

    @abstractmethod
    async def delete(self, comment_id: int) -> bool:
        pass

    @abstractmethod
    async def find_by_review(self, review_id: int) -> list[Comment]:
        pass


class FollowRepository(ABC):
    @abstractmethod
    async def save(self, follow: Follow) -> Follow:
        pass

    @abstractmethod
    async def delete(
        self, follower_id: int, target_type: EnumFollowTarget, target_id: int
    ) -> bool:
        pass

    @abstractmethod
    async def exists(
        self, follower_id: int, target_type: EnumFollowTarget, target_id: int
    ) -> bool:
        pass

    @abstractmethod
    async def find_by_follower(
        self, follower_id: int, target_type: EnumFollowTarget | None = None
    ) -> list[Follow]:
        pass

    @abstractmethod
    async def count_followers(
        self, target_type: EnumFollowTarget, target_id: int
    ) -> int:
        pass


class NotificationRepository(ABC):
    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def find_by_user(self, user_id: int, limit: int = 50) -> list[Notification]:
        pass

    @abstractmethod
    async def count_unread(self, user_id: int) -> int:
        pass

    @abstractmethod
    async def mark_read(self, user_id: int, notification_id: int) -> bool:
        pass

    @abstractmethod
    async def mark_all_read(self, user_id: int) -> None:
        pass


class NotificationPreferenceRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> NotificationPreference:
        pass

    @abstractmethod
    async def save(self, preference: NotificationPreference) -> NotificationPreference:
        pass
