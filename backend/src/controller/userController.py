from http import HTTPStatus

from sqlite3 import IntegrityError

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException

from database import get_session
from schema.schemas import (
    UserListSchema,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)
from model.models import User
from security import get_password_hash, get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/", status_code=HTTPStatus.OK, response_model=UserListSchema)
async def get_users(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    users = await session.scalars(select(User).offset(offset).limit(limit))
    return {"users": users}


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
async def create_user(user: UserSchema, session: AsyncSession = Depends(get_session)):
    db_user = await session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail="Email already registered"
            )
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail="Username already registered"
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


# Suggestion: Enviar um email de confirmação antes de atualizar o usuário, e só atualizar se o email for confirmado.
@router.put("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublicSchema)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You can only update your own user"
        )
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or email already registered",
        )


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You can only delete your own user"
        )
    await session.delete(current_user)
    await session.commit()

    return {"message": "User deleted successfully"}
