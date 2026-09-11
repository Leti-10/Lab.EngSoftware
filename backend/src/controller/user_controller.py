from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.user import User
from src.schemas.user import UserCreate, UserList, UserPublic
from src.security import get_current_user
from src.services.user_service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    list_users,
    update_user as update_user_service,
)

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/", status_code=HTTPStatus.OK, response_model=UserList)
async def get_users(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    users = await list_users(session, limit, offset)
    return {"users": users}


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        return await create_user_service(session, user)
    except ValueError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=str(error)
        ) from error


# Suggestion: Enviar um email de confirmação antes de atualizar o usuário, e só atualizar se o email for confirmado.
@router.put("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You can only update your own user"
        )
    try:
        return await update_user_service(session, current_user, user)
    except ValueError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=str(error)
        ) from error


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You can only delete your own user"
        )
    await delete_user_service(session, current_user)
