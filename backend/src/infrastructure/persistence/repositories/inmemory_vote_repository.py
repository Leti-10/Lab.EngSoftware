from src.domain.entities import Vote
from src.domain.enums.enums import EnumVoteTarget
from src.domain.exceptions import VoteAlreadyExistsError
from src.domain.repositories import VoteRepository


class InMemoryVoteRepository(VoteRepository):
    def __init__(
        self,
        user_names: dict[int, str] | None = None,
        target_names: dict[tuple[EnumVoteTarget, int], str] | None = None,
    ):
        self.votes: dict[int, Vote] = {}
        self._next_id = 1
        self.user_names = user_names or {}
        self.target_names = target_names or {}

    async def save(self, vote: Vote) -> Vote:
        if any(
            existing_vote.id != vote.id
            and existing_vote.user_id == vote.user_id
            and existing_vote.target_entity == vote.target_entity
            and existing_vote.target_id == vote.target_id
            for existing_vote in self.votes.values()
        ):
            raise VoteAlreadyExistsError()

        if vote.id is None:
            vote.id = self._next_id
            self._next_id += 1
        self.votes[vote.id] = vote
        return vote

    async def get_by_id(self, vote_id: int) -> Vote | None:
        return self.votes.get(vote_id)

    async def delete(self, vote_id: int) -> bool:
        return self.votes.pop(vote_id, None) is not None

    async def find_by_filter(
        self,
        status: str | None = None,
        user_name: str | None = None,
        target_type: EnumVoteTarget | None = None,
        target_name: str | None = None,
    ) -> list[Vote]:
        normalized_user_name = user_name.casefold() if user_name else None
        normalized_target_name = target_name.casefold() if target_name else None
        return [
            vote
            for vote in self.votes.values()
            if (status is None or vote.status == status)
            and (
                normalized_user_name is None
                or normalized_user_name
                in self.user_names.get(vote.user_id, "").casefold()
            )
            and (target_type is None or vote.target_entity == target_type)
            and (
                normalized_target_name is None
                or normalized_target_name
                in self.target_names.get(
                    (vote.target_entity, vote.target_id), ""
                ).casefold()
            )
        ]