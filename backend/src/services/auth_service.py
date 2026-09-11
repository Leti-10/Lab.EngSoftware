from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.security import create_access_token, verify_password


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> str | None:
    user = await session.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password):
        return None
    return create_access_token(data={"sub": user.email})
