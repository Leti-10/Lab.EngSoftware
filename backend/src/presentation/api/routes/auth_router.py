from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases import AuthenticateUserUseCase, CreateUserUseCase
from src.domain.entities import User
from src.domain.exceptions import InvalidCredentialsError
from src.domain.repositories import UserRepository
from src.infrastructure.security.token_service import TokenService
from src.presentation.api.dependencies import get_current_user, get_user_repository
from src.presentation.api.schemas import (
    LoginSchema,
    RegisterSchema,
    TokenResponseSchema,
    UserResponseSchema,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _to_response(user: User) -> UserResponseSchema:
    return UserResponseSchema(
        id=user.id, username=user.username, email=user.email, role=user.role
    )


def _to_token(user: User) -> TokenResponseSchema:
    return TokenResponseSchema(
        access_token=TokenService.create_access_token(user.id),
        user=_to_response(user),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterSchema,
    repository: UserRepository = Depends(get_user_repository),
) -> TokenResponseSchema:
    try:
        user = CreateUserUseCase(repository).execute(
            username=payload.username.strip(),
            email=payload.email.strip().lower(),
            password=payload.password,
        )
    except ValueError as error:
        conflict = str(error) == "E-mail já cadastrado"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if conflict
            else status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return _to_token(user)


@router.post("/login")
def login(
    payload: LoginSchema,
    repository: UserRepository = Depends(get_user_repository),
) -> TokenResponseSchema:
    try:
        user = AuthenticateUserUseCase(repository).execute(
            email=payload.email.strip().lower(), password=payload.password
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=error.message
        ) from error

    return _to_token(user)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)) -> UserResponseSchema:
    return _to_response(current_user)
