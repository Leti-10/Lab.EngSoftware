from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.user_model import User


class UserRepository:

    @staticmethod
    async def get_users(
        session: AsyncSession,
        limit: int,
        offset: int,
    ):
        result = await session.scalars(
            select(User)
            .offset(offset)
            .limit(limit)
        )

        return result.all()

    @staticmethod
    async def get_by_email_or_username(
        session: AsyncSession,
        email: str,
        username: str,
    ):
        return await session.scalar(
            select(User).where(
                (User.email == email) |
                (User.username == username)
            )
        )

    @staticmethod
    async def create(
        session: AsyncSession,
        user: User,
    ):
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def update(
        session: AsyncSession,
        user: User,
    ):
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def delete(
        session: AsyncSession,
        user: User,
    ):
        await session.delete(user)
        await session.commit()