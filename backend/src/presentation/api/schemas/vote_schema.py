from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.enums.enums import VoteTarget


class CreateVoteSchema(BaseModel):
    status: str = Field(..., min_length=1)
    target_entity: VoteTarget
    target_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)

    @field_validator("status")
    @classmethod
    def strip_status(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("O status do voto não pode ser vazio.")
        return cleaned


class VoteResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    status: str
    target_entity: VoteTarget
    target_id: int
    user_id: int
