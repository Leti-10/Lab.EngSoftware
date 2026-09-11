from datetime import datetime, timedelta, timezone

from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jwt import DecodeError, decode, encode, ExpiredSignatureError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pwdlib import PasswordHash

from src.models.user import User
from src.database import get_session
from src.settings import Settings

pwd_context = PasswordHash.recommended()
settings = Settings()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encode_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject_email = payload.get("sub")
        if not subject_email:
            raise credentials_exception

    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    user = await session.scalar(select(User).where(User.email == subject_email))
    if not user:
        raise credentials_exception

    return user
