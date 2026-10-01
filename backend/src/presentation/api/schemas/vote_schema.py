from pydantic import BaseModel, Field

from src.domain.enums.enums import VoteTarget


class CreateVoteSchema(BaseModel):
    status: str
    target_entity: VoteTarget | str
    target_id: int
    user_id: int
