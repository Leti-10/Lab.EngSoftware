from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from fastapi import Depends, HTTPException, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode, ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from src.model.models import User
from src.database import get_session

SECRET_KEY = "capivaras_sao_demais_e_sensacionais"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = PasswordHash.recommended()

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encode_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_email = payload.get("sub")
        if not subject_email:
            raise credentials_exception

    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == subject_email))
    if not user:
        raise credentials_exception

    return user