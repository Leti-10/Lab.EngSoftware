from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users: list[User] = []
        self._last_id = 0

    def save(self, user: User) -> User:
        self._last_id += 1
        user.id = self._last_id
        self.users.append(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_by_email(self, email: str) -> User | None:
        for user in self.users:
            if user.email == email:
                return user
        return None
