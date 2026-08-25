from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from model.models import User
from schema.schemas import TokenSchema
from security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/", response_model=TokenSchema)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await session.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
