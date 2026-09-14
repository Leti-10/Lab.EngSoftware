from abc import ABC, abstractmethod
from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass
