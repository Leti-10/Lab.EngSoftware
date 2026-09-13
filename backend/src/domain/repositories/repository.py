from abc import ABC, abstractmethod
from typing import List, Optional
from backend.src.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass