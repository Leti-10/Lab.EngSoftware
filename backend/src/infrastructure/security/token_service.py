from datetime import datetime, timedelta, timezone

import jwt

from src.core.config import settings


class TokenService:
    @staticmethod
    def create_access_token(user_id: int) -> str:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {"sub": str(user_id), "exp": expires}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_user_id(token: str) -> int | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return int(payload["sub"])
        except (jwt.PyJWTError, KeyError, ValueError):
            return None
