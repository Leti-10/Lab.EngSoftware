from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.entities import User
from src.domain.enums.enums import EnumFollowTarget
from src.domain.repositories import BookListRepository, BookRepository, UserRepository
from src.domain.repositories.social_repository import FollowRepository
from src.presentation.api.dependencies import (
    get_follow_repository,
    get_optional_user,
    get_user_repository,
)
from src.presentation.api.routes.book_list_router import (
    _to_response as list_to_response,
    get_book_list_repository,
)
from src.presentation.api.routes.book_router import get_book_repository
from src.presentation.api.schemas import BookListResponseSchema
from src.presentation.api.schemas.social_schema import PublicProfileSchema

router = APIRouter(prefix="/users", tags=["Users"])


async def _require_user(user_id: int, users: UserRepository) -> User:
    user = await users.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    return user


@router.get("/{user_id}")
async def get_public_profile(
    user_id: int,
    users: UserRepository = Depends(get_user_repository),
    follows: FollowRepository = Depends(get_follow_repository),
    viewer: User | None = Depends(get_optional_user),
) -> PublicProfileSchema:
    user = await _require_user(user_id, users)
    following = await follows.find_by_follower(user.id, EnumFollowTarget.USER)
    return PublicProfileSchema(
        id=user.id,
        username=user.username,
        bio=user.bio,
        avatar_url=user.avatar_url,
        cover_url=user.cover_url,
        followers=await follows.count_followers(EnumFollowTarget.USER, user.id),
        following=len(following),
        is_following=(
            await follows.exists(viewer.id, EnumFollowTarget.USER, user.id)
            if viewer is not None
            else False
        ),
    )


@router.get("/{user_id}/lists")
async def get_public_lists(
    user_id: int,
    users: UserRepository = Depends(get_user_repository),
    lists: BookListRepository = Depends(get_book_list_repository),
    books: BookRepository = Depends(get_book_repository),
) -> list[BookListResponseSchema]:
    await _require_user(user_id, users)
    public = [item for item in lists.list_by_owner(user_id) if not item.private]
    return [await list_to_response(item, books) for item in public]
