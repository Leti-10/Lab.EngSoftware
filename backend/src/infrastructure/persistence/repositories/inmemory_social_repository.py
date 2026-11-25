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


class InMemoryCommentRepository(CommentRepository):
    def __init__(self):
        self.comments: dict[int, Comment] = {}
        self._next_id = 1

    async def save(self, comment: Comment) -> Comment:
        comment.id = self._next_id
        self._next_id += 1
        self.comments[comment.id] = comment
        return comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        return self.comments.get(comment_id)

    async def delete(self, comment_id: int) -> bool:
        return self.comments.pop(comment_id, None) is not None

    async def find_by_review(self, review_id: int) -> list[Comment]:
        return [c for c in self.comments.values() if c.review_id == review_id]


class InMemoryFollowRepository(FollowRepository):
    def __init__(self):
        self.follows: list[Follow] = []
        self._next_id = 1

    def _find(self, follower_id, target_type, target_id) -> Follow | None:
        for follow in self.follows:
            if (
                follow.follower_id == follower_id
                and follow.target_type == target_type
                and follow.target_id == target_id
            ):
                return follow
        return None

    async def save(self, follow: Follow) -> Follow:
        existing = self._find(follow.follower_id, follow.target_type, follow.target_id)
        if existing is not None:
            return existing
        follow.id = self._next_id
        self._next_id += 1
        self.follows.append(follow)
        return follow

    async def delete(self, follower_id, target_type, target_id) -> bool:
        existing = self._find(follower_id, target_type, target_id)
        if existing is None:
            return False
        self.follows.remove(existing)
        return True

    async def exists(self, follower_id, target_type, target_id) -> bool:
        return self._find(follower_id, target_type, target_id) is not None

    async def find_by_follower(self, follower_id, target_type=None) -> list[Follow]:
        return [
            f
            for f in self.follows
            if f.follower_id == follower_id
            and (target_type is None or f.target_type == target_type)
        ]

    async def count_followers(
        self, target_type: EnumFollowTarget, target_id: int
    ) -> int:
        return sum(
            1
            for f in self.follows
            if f.target_type == target_type and f.target_id == target_id
        )


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self):
        self.notifications: dict[int, Notification] = {}
        self._next_id = 1

    async def save(self, notification: Notification) -> Notification:
        notification.id = self._next_id
        self._next_id += 1
        self.notifications[notification.id] = notification
        return notification

    async def find_by_user(self, user_id: int, limit: int = 50) -> list[Notification]:
        mine = [n for n in self.notifications.values() if n.user_id == user_id]
        return sorted(mine, key=lambda n: n.id, reverse=True)[:limit]

    async def count_unread(self, user_id: int) -> int:
        return sum(
            1
            for n in self.notifications.values()
            if n.user_id == user_id and not n.read
        )

    async def mark_read(self, user_id: int, notification_id: int) -> bool:
        notification = self.notifications.get(notification_id)
        if notification is None or notification.user_id != user_id:
            return False
        notification.read = True
        return True

    async def mark_all_read(self, user_id: int) -> None:
        for notification in self.notifications.values():
            if notification.user_id == user_id:
                notification.read = True


class InMemoryNotificationPreferenceRepository(NotificationPreferenceRepository):
    def __init__(self):
        self.preferences: dict[int, NotificationPreference] = {}

    async def get(self, user_id: int) -> NotificationPreference:
        return self.preferences.get(user_id) or NotificationPreference(user_id=user_id)

    async def save(self, preference: NotificationPreference) -> NotificationPreference:
        self.preferences[preference.user_id] = preference
        return preference
