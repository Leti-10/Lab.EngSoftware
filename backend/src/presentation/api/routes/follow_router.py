from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.social import (
    FollowUseCase,
    ListFollowingUseCase,
    NotifyUseCase,
    UnfollowUseCase,
)
from src.domain.entities import User
from src.domain.enums.enums import EnumFollowTarget, EnumNotificationType
from src.domain.exceptions import InvalidFollowError
from src.domain.repositories import BookListRepository, UserRepository
from src.domain.repositories.social_repository import (
    FollowRepository,
    NotificationPreferenceRepository,
    NotificationRepository,
)
from src.presentation.api.dependencies import (
    get_current_user,
    get_follow_repository,
    get_notification_preference_repository,
    get_notification_repository,
    get_optional_user,
    get_user_repository,
)
from src.presentation.api.routes.book_list_router import get_book_list_repository
from src.presentation.api.schemas.social_schema import (
    FollowItemSchema,
    FollowStatusSchema,
)

router = APIRouter(prefix="/follows", tags=["Follows"])


async def _require_target(
    target_type: EnumFollowTarget,
    target_id: int,
    users: UserRepository,
    lists: BookListRepository,
    viewer: User | None,
) -> None:
    if target_type == EnumFollowTarget.USER:
        found = await users.get_by_id(target_id) is not None
    else:
        book_list = lists.get_by_id(target_id)
        found = book_list is not None and (
            not book_list.private
            or (viewer is not None and book_list.owner == viewer.id)
        )
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alvo não encontrado."
        )


async def _status(
    follows: FollowRepository,
    viewer: User | None,
    target_type: EnumFollowTarget,
    target_id: int,
) -> FollowStatusSchema:
    following = (
        await follows.exists(viewer.id, target_type, target_id)
        if viewer is not None
        else False
    )
    return FollowStatusSchema(
        following=following,
        followers=await follows.count_followers(target_type, target_id),
    )


@router.get("")
async def list_my_follows(
    type: EnumFollowTarget | None = None,
    follows: FollowRepository = Depends(get_follow_repository),
    current_user: User = Depends(get_current_user),
) -> list[FollowItemSchema]:
    found = await ListFollowingUseCase(follows).execute(current_user.id, type)
    return [
        FollowItemSchema(target_type=item.target_type, target_id=item.target_id)
        for item in found
    ]


@router.get("/{target_type}/{target_id}")
async def follow_status(
    target_type: EnumFollowTarget,
    target_id: int,
    follows: FollowRepository = Depends(get_follow_repository),
    viewer: User | None = Depends(get_optional_user),
) -> FollowStatusSchema:
    return await _status(follows, viewer, target_type, target_id)


@router.put("/{target_type}/{target_id}")
async def follow(
    target_type: EnumFollowTarget,
    target_id: int,
    follows: FollowRepository = Depends(get_follow_repository),
    users: UserRepository = Depends(get_user_repository),
    lists: BookListRepository = Depends(get_book_list_repository),
    notifications: NotificationRepository = Depends(get_notification_repository),
    preferences: NotificationPreferenceRepository = Depends(
        get_notification_preference_repository
    ),
    current_user: User = Depends(get_current_user),
) -> FollowStatusSchema:
    await _require_target(target_type, target_id, users, lists, current_user)
    try:
        _, created = await FollowUseCase(follows).execute(
            current_user.id, target_type, target_id
        )
    except InvalidFollowError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.message
        ) from error

    if created and target_type == EnumFollowTarget.USER:
        await NotifyUseCase(notifications, preferences).execute(
            target_id, current_user.id, EnumNotificationType.FOLLOW
        )
    return await _status(follows, current_user, target_type, target_id)


@router.delete("/{target_type}/{target_id}")
async def unfollow(
    target_type: EnumFollowTarget,
    target_id: int,
    follows: FollowRepository = Depends(get_follow_repository),
    current_user: User = Depends(get_current_user),
) -> FollowStatusSchema:
    await UnfollowUseCase(follows).execute(current_user.id, target_type, target_id)
    return await _status(follows, current_user, target_type, target_id)
