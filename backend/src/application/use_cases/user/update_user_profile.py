from src.domain.entities import User
from src.domain.repositories import UserRepository


class UpdateUserProfileUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self,
        user: User,
        bio: str | None,
        avatar_url: str | None,
        cover_url: str | None,
    ) -> User:
        user.update_profile(bio, avatar_url, cover_url)
        return await self.user_repository.update(user)
