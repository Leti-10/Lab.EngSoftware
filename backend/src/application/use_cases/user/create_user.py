from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.security.password_hasher import PasswordHasher


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(
        self, username: str, email: str, password: str, role: str = "user"
    ) -> User:
        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise ValueError("E-mail já cadastrado")

        user = User(
            username=username,
            email=email,
            password=PasswordHasher.hash_password(password),
            role=role,
        )

        saved_user = self.user_repository.save(user)

        return saved_user
