from pydantic import BaseModel, ConfigDict, Field


class CreateReportSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    target_id: int = Field(..., gt=0)
    target_entity: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=1000)


class ReportResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    user_id: int
    target_id: int
    target_entity: str
    description: str
