from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from src.application.use_cases import (
    AuthenticateUserUseCase,
    CreateUserUseCase,
    UpdateUserProfileUseCase,
)
from src.core import settings
from src.domain.entities import User
from src.domain.exceptions import InvalidCredentialsError
from src.domain.repositories import UserRepository
from src.infrastructure.security.token_service import (
    ACCESS_TOKEN_COOKIE_NAME,
    TokenService,
)
from src.presentation.api.dependencies import get_current_user, get_user_repository
from src.presentation.api.schemas import (
    AuthResponseSchema,
    LoginSchema,
    RegisterSchema,
    UpdateProfileSchema,
    UserResponseSchema,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _to_response(user: User) -> UserResponseSchema:
    return UserResponseSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        bio=user.bio,
        avatar_url=user.avatar_url,
        cover_url=user.cover_url,
    )


def _set_auth_cookie(response: Response, user: User) -> AuthResponseSchema:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=TokenService.create_access_token(user.id),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return AuthResponseSchema(user=_to_response(user))


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterSchema,
    response: Response,
    repository: UserRepository = Depends(get_user_repository),
) -> AuthResponseSchema:
    try:
        user = await CreateUserUseCase(repository).execute(
            username=payload.username.strip(),
            email=payload.email.strip().lower(),
            password=payload.password,
        )
    except ValueError as error:
        conflict = str(error) == "E-mail já cadastrado"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if conflict
            else status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail ou username já cadastrado.",
        ) from error

    return _set_auth_cookie(response, user)


@router.post("/login")
async def login(
    payload: LoginSchema,
    response: Response,
    repository: UserRepository = Depends(get_user_repository),
) -> AuthResponseSchema:
    try:
        user = await AuthenticateUserUseCase(repository).execute(
            email=payload.email.strip().lower(), password=payload.password
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=error.message
        ) from error

    return _set_auth_cookie(response, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    _clear_auth_cookie(response)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)) -> UserResponseSchema:
    return _to_response(current_user)


@router.put("/me")
async def update_me(
    payload: UpdateProfileSchema,
    current_user: User = Depends(get_current_user),
    repository: UserRepository = Depends(get_user_repository),
) -> UserResponseSchema:
    try:
        updated = await UpdateUserProfileUseCase(repository).execute(
            current_user,
            bio=payload.bio,
            avatar_url=payload.avatar_url,
            cover_url=payload.cover_url,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    return _to_response(updated)
