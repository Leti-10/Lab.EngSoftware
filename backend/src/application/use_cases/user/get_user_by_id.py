from src.domain.entities import User
from src.domain.repositories import UserRepository


class GetUserByIdUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: int) -> User | None:
        return await self.user_repository.get_by_id(user_id)
