from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.persistence.models.user_model import UserModelSQLAlchemy


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> User:
        model = UserModelSQLAlchemy(
            username=user.username,
            email=user.email,
            password=user.password,
            role=user.role,
            created_at=user.created_at,
        )
        self.session.add(model)
        try:
            await self.session.commit()
            await self.session.refresh(model)
        except IntegrityError:
            await self.session.rollback()
            raise

        user.id = model.id
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(UserModelSQLAlchemy).where(UserModelSQLAlchemy.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(UserModelSQLAlchemy).where(UserModelSQLAlchemy.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    @staticmethod
    def _to_domain(model: UserModelSQLAlchemy) -> User:
        user = User(
            username=model.username,
            email=model.email,
            password=model.password,
            role=model.role,
            created_at=model.created_at,
        )
        user.id = model.id
        return user
