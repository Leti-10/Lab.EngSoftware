from dataclasses import dataclass, field

from src.domain.enums.enums import VoteTarget
from src.domain.exceptions import (
    InvalidVoteStatusError,
    InvalidVoteTargetError,
    InvalidVoteUserError,
)


@dataclass
class Vote:
    id: int | None = field(default=None)
    status: str = field(default="")
    target_entity: VoteTarget | str = field(default="")
    target_id: int = field(default=0)
    user_id: int = field(default=0)

    def __post_init__(self):
        if not self.status.strip():
            raise InvalidVoteStatusError()

        if not isinstance(self.target_entity, VoteTarget):
            try:
                self.target_entity = VoteTarget(self.target_entity)
            except ValueError:
                raise InvalidVoteTargetError(self.target_entity)

        if self.target_id <= 0:
            raise InvalidVoteTargetError(self.target_id)

        if self.user_id <= 0:
            raise InvalidVoteUserError(self.user_id)
