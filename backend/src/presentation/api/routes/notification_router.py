from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.social import (
    GetNotificationPreferencesUseCase,
    ListNotificationsUseCase,
    MarkNotificationsReadUseCase,
    UpdateNotificationPreferencesUseCase,
)
from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.domain.repositories.social_repository import (
    NotificationPreferenceRepository,
    NotificationRepository,
)
from src.presentation.api.dependencies import (
    get_current_user,
    get_notification_preference_repository,
    get_notification_repository,
    get_user_repository,
)
from src.presentation.api.schemas.social_schema import (
    NotificationListSchema,
    NotificationPreferenceSchema,
    NotificationResponseSchema,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    repository: NotificationRepository = Depends(get_notification_repository),
    users: UserRepository = Depends(get_user_repository),
    current_user: User = Depends(get_current_user),
) -> NotificationListSchema:
    items, unread = await ListNotificationsUseCase(repository).execute(current_user.id)
    usernames: dict[int, str | None] = {}
    responses = []
    for item in items:
        if item.actor_id not in usernames:
            actor = await users.get_by_id(item.actor_id)
            usernames[item.actor_id] = actor.username if actor else None
        responses.append(
            NotificationResponseSchema(
                id=item.id,
                type=item.type,
                actor_id=item.actor_id,
                actor_username=usernames[item.actor_id],
                review_id=item.review_id,
                book_id=item.book_id,
                read=item.read,
                created_at=item.created_at,
            )
        )
    return NotificationListSchema(items=responses, unread=unread)


@router.post("/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    repository: NotificationRepository = Depends(get_notification_repository),
    current_user: User = Depends(get_current_user),
) -> None:
    await MarkNotificationsReadUseCase(repository).execute(current_user.id)


@router.get("/preferences")
async def get_preferences(
    repository: NotificationPreferenceRepository = Depends(
        get_notification_preference_repository
    ),
    current_user: User = Depends(get_current_user),
) -> NotificationPreferenceSchema:
    preference = await GetNotificationPreferencesUseCase(repository).execute(
        current_user.id
    )
    return NotificationPreferenceSchema(
        likes=preference.likes,
        comments=preference.comments,
        follows=preference.follows,
    )


@router.put("/preferences")
async def update_preferences(
    payload: NotificationPreferenceSchema,
    repository: NotificationPreferenceRepository = Depends(
        get_notification_preference_repository
    ),
    current_user: User = Depends(get_current_user),
) -> NotificationPreferenceSchema:
    saved = await UpdateNotificationPreferencesUseCase(repository).execute(
        current_user.id, payload.likes, payload.comments, payload.follows
    )
    return NotificationPreferenceSchema(
        likes=saved.likes, comments=saved.comments, follows=saved.follows
    )


@router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    notification_id: int,
    repository: NotificationRepository = Depends(get_notification_repository),
    current_user: User = Depends(get_current_user),
) -> None:
    found = await MarkNotificationsReadUseCase(repository).execute(
        current_user.id, notification_id
    )
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada."
        )
