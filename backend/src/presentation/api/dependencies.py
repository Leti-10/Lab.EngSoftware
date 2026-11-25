from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.domain.repositories.review_repository import ReviewRepository
from src.domain.repositories.social_repository import (
    CommentRepository,
    FollowRepository,
    NotificationPreferenceRepository,
    NotificationRepository,
)
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import (
    SQLAlchemyCommentRepository,
    SQLAlchemyFollowRepository,
    SQLAlchemyNotificationPreferenceRepository,
    SQLAlchemyNotificationRepository,
    SQLAlchemyReviewRepository,
    SQLAlchemyUserRepository,
)
from src.infrastructure.security.token_service import TokenService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_repository(
    session: AsyncSession = Depends(get_db_context),
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_review_repository(
    session: AsyncSession = Depends(get_db_context),
) -> ReviewRepository:
    return SQLAlchemyReviewRepository(session)


async def get_comment_repository(
    session: AsyncSession = Depends(get_db_context),
) -> CommentRepository:
    return SQLAlchemyCommentRepository(session)


async def get_follow_repository(
    session: AsyncSession = Depends(get_db_context),
) -> FollowRepository:
    return SQLAlchemyFollowRepository(session)


async def get_notification_repository(
    session: AsyncSession = Depends(get_db_context),
) -> NotificationRepository:
    return SQLAlchemyNotificationRepository(session)


async def get_notification_preference_repository(
    session: AsyncSession = Depends(get_db_context),
) -> NotificationPreferenceRepository:
    return SQLAlchemyNotificationPreferenceRepository(session)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repository: UserRepository = Depends(get_user_repository),
) -> User | None:
    if credentials is None:
        return None
    user_id = TokenService.decode_user_id(credentials.credentials)
    return await repository.get_by_id(user_id) if user_id is not None else None


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
