from src.domain.entities import User
from src.domain.exceptions import InvalidCredentialsError
from src.domain.repositories import UserRepository
from src.infrastructure.security.password_hasher import PasswordHasher


class AuthenticateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)

        if user is None or not PasswordHasher.verify_password(password, user.password):
            raise InvalidCredentialsError()

        return user
