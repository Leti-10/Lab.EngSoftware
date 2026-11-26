from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateReviewSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    isSpoiler: bool = False
    book_id: int = Field(..., gt=0)


class UpdateReviewSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    isSpoiler: bool = False


class UpdateReviewSpoilerSchema(BaseModel):
    isSpoiler: bool


class ReviewResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    rating: int
    comment: str | None
    isSpoiler: bool
    user_id: int
    book_id: int
    created_at: datetime
    username: str | None = None
    likes: int = 0
    liked_by_me: bool = False
    like_vote_id: int | None = None
