from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.schema import TokenSchema
from src.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/", response_model=TokenSchema)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    access_token = await authenticate_user(
        session, form_data.username, form_data.password
    )
    if access_token is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect username or password"
        )

    return {"access_token": access_token, "token_type": "bearer"}
