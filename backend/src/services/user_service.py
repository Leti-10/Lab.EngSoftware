from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.user import UserCreate
from src.security import get_password_hash


async def list_users(session: AsyncSession, limit: int, offset: int) -> list[User]:
    result = await session.scalars(select(User).offset(offset).limit(limit))
    return list(result.all())


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    existing = await session.scalar(
        select(User).where(
            (User.email == data.email) | (User.username == data.username)
        )
    )
    if existing:
        if existing.email == data.email:
            raise ValueError("Email already registered")
        raise ValueError("Username already registered")

    user = User(
        username=data.username,
        email=data.email,
        password=get_password_hash(data.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Username or email already registered") from None
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, data: UserCreate) -> User:
    user.username = data.username
    user.email = data.email
    user.password = get_password_hash(data.password)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Username or email already registered") from None
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()
