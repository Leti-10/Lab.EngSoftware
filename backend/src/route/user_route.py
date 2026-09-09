from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from controller.userController import (
    create_user,
    delete_user,
    get_users,
    update_user,
)
from database import get_session
from model.user_model import User
from schema.schemas import (
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)
from security import get_current_user


router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=UserListSchema,
)
async def get_users_route(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await get_users(
        limit,
        offset,
        session,
    )


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublicSchema,
)
async def create_user_route(
    user: UserSchema,
    session: AsyncSession = Depends(get_session),
):
    return await create_user(
        user,
        session,
    )


@router.put(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
async def update_user_route(
    user_id: int,
    user: UserSchema,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await update_user(
        user_id,
        user,
        session,
        current_user,
    )


@router.delete(
    "/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_user_route(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await delete_user(
        user_id,
        session,
        current_user,
    )