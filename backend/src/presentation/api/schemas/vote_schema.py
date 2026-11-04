from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.enums import EnumVoteTarget


class CreateVoteSchema(BaseModel):
    status: str = Field(..., min_length=1)
    target_entity: EnumVoteTarget
    target_id: int = Field(..., gt=0)
    user_id: int | None = Field(default=None, gt=0)

    @field_validator("status")
    @classmethod
    def strip_status(cls, value: str) -> str:
        _cleaned = value.strip()
        if not _cleaned:
            raise ValueError("O status do voto não pode ser vazio.")
        return _cleaned


class VoteResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    status: str
    target_entity: EnumVoteTarget
    target_id: int
    user_id: int
