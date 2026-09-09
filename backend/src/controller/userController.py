from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from model.user_model import User
from schema.schemas import (
    UserSchema,
)
from service.user_service import UserService


service = UserService()


async def get_users(
    limit: int,
    offset: int,
    session: AsyncSession,
):
    users = await service.get_users(
        session,
        limit,
        offset,
    )

    return {"users": users}


async def create_user(
    user: UserSchema,
    session: AsyncSession,
):
    try:
        return await service.create_user(
            session,
            user,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from None


async def update_user(
    user_id: int,
    user: UserSchema,
    session: AsyncSession,
    current_user: User,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You can only update your own user",
        )

    try:
        return await service.update_user(
            session,
            current_user,
            user,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or email already registered",
        ) from None


async def delete_user(
    user_id: int,
    session: AsyncSession,
    current_user: User,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You can only delete your own user",
        )

    await service.delete_user(
        session,
        current_user,
    )