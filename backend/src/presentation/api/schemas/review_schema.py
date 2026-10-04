from pydantic import BaseModel, ConfigDict, Field


class CreateReviewSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    user_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)


class ReviewResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    rating: int
    comment: str | None
    user_id: int
    book_id: int
