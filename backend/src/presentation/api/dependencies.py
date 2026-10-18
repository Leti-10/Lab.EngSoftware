from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import SQLAlchemyUserRepository
from src.infrastructure.security.token_service import TokenService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_repository(
    session: AsyncSession = Depends(get_db_context),
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    user_id = TokenService.decode_user_id(credentials.credentials)
    user = await repository.get_by_id(user_id) if user_id is not None else None
    if user is None:
        raise unauthorized
    return user
