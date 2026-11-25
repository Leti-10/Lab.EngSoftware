from src.domain.entities.review import Review
from src.domain.entities.social import Follow
from src.domain.enums.enums import EnumFollowTarget
from src.domain.repositories.review_repository import ReviewRepository
from src.domain.repositories.social_repository import FollowRepository

FEED_LIMIT = 30


class FollowUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self.follow_repository = follow_repository

    async def execute(
        self, follower_id: int, target_type: EnumFollowTarget, target_id: int
    ) -> tuple[Follow, bool]:
        already = await self.follow_repository.exists(
            follower_id, target_type, target_id
        )
        follow = await self.follow_repository.save(
            Follow(
                follower_id=follower_id, target_type=target_type, target_id=target_id
            )
        )
        return follow, not already


class UnfollowUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self.follow_repository = follow_repository

    async def execute(
        self, follower_id: int, target_type: EnumFollowTarget, target_id: int
    ) -> bool:
        return await self.follow_repository.delete(follower_id, target_type, target_id)


class ListFollowingUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self.follow_repository = follow_repository

    async def execute(
        self, follower_id: int, target_type: EnumFollowTarget | None = None
    ) -> list[Follow]:
        return await self.follow_repository.find_by_follower(follower_id, target_type)


class BuildFeedUseCase:
    def __init__(
        self, follow_repository: FollowRepository, review_repository: ReviewRepository
    ):
        self.follow_repository = follow_repository
        self.review_repository = review_repository

    async def execute(self, user_id: int, limit: int = FEED_LIMIT) -> list[Review]:
        followed = await self.follow_repository.find_by_follower(
            user_id, EnumFollowTarget.USER
        )
        reviews: list[Review] = []
        for follow in followed:
            reviews.extend(
                await self.review_repository.find_by_filter(user_id=follow.target_id)
            )
        return sorted(reviews, key=lambda review: review.id or 0, reverse=True)[:limit]
