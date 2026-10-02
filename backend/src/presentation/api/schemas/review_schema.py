from pydantic import BaseModel, Field


class CreateReviewSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    user_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)
