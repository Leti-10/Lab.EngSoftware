from src.domain.entities.social import Notification, NotificationPreference
from src.domain.enums.enums import EnumNotificationType
from src.domain.repositories.social_repository import (
    NotificationPreferenceRepository,
    NotificationRepository,
)


class NotifyUseCase:
    def __init__(
        self,
        notification_repository: NotificationRepository,
        preference_repository: NotificationPreferenceRepository,
    ):
        self.notification_repository = notification_repository
        self.preference_repository = preference_repository

    async def execute(
        self,
        recipient_id: int,
        actor_id: int,
        kind: EnumNotificationType,
        review_id: int | None = None,
        book_id: int | None = None,
    ) -> Notification | None:
        if recipient_id == actor_id:
            return None
        preference = await self.preference_repository.get(recipient_id)
        if not preference.allows(kind):
            return None
        return await self.notification_repository.save(
            Notification(
                user_id=recipient_id,
                type=kind,
                actor_id=actor_id,
                review_id=review_id,
                book_id=book_id,
            )
        )


class ListNotificationsUseCase:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    async def execute(self, user_id: int) -> tuple[list[Notification], int]:
        items = await self.notification_repository.find_by_user(user_id)
        unread = await self.notification_repository.count_unread(user_id)
        return items, unread


class MarkNotificationsReadUseCase:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    async def execute(self, user_id: int, notification_id: int | None = None) -> bool:
        if notification_id is None:
            await self.notification_repository.mark_all_read(user_id)
            return True
        return await self.notification_repository.mark_read(user_id, notification_id)


class GetNotificationPreferencesUseCase:
    def __init__(self, preference_repository: NotificationPreferenceRepository):
        self.preference_repository = preference_repository

    async def execute(self, user_id: int) -> NotificationPreference:
        return await self.preference_repository.get(user_id)


class UpdateNotificationPreferencesUseCase:
    def __init__(self, preference_repository: NotificationPreferenceRepository):
        self.preference_repository = preference_repository

    async def execute(
        self, user_id: int, likes: bool, comments: bool, follows: bool
    ) -> NotificationPreference:
        return await self.preference_repository.save(
            NotificationPreference(
                user_id=user_id, likes=likes, comments=comments, follows=follows
            )
        )
