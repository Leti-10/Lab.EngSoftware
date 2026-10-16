from src.domain.entities import Vote
from src.domain.enums.enums import EnumVoteTarget
from src.domain.repositories import VoteRepository


class FilterVotesUseCase:
    def __init__(self, vote_repository: VoteRepository):
        self.vote_repository = vote_repository

    async def execute(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: EnumVoteTarget | None = None,
        target_name: str | None = None,
    ) -> list[Vote]:
        return await self.vote_repository.find_by_filter(
            status=status,
            user_name=user_name,
            target_type=target_type,
            target_name=target_name,
        )
