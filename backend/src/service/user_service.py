from sqlalchemy.ext.asyncio import AsyncSession

from model.user_model import User
from repository.user_repository import UserRepository
from schema.schemas import UserSchema
from security import get_password_hash


class UserService:
    @staticmethod
    async def get_users(
        session: AsyncSession,
        limit: int,
        offset: int,
    ):
        return await UserRepository.get_users(
            session,
            limit,
            offset,
        )

    @staticmethod
    async def create_user(
        session: AsyncSession,
        user: UserSchema,
    ):
        db_user = await UserRepository.get_by_email_or_username(
            session,
            user.email,
            user.username,
        )

        if db_user:
            if db_user.email == user.email:
                raise ValueError("Email already registered")

            if db_user.username == user.username:
                raise ValueError("Username already registered")

        db_user = User(
            username=user.username,
            email=user.email,
            password=get_password_hash(user.password),
        )

        return await UserRepository.create(
            session,
            db_user,
        )

    @staticmethod
    async def update_user(
        session: AsyncSession,
        current_user: User,
        user: UserSchema,
    ):
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        return await UserRepository.update(
            session,
            current_user,
        )

    @staticmethod
    async def delete_user(
        session: AsyncSession,
        current_user: User,
    ):
        await UserRepository.delete(
            session,
            current_user,
        )
