from datetime import datetime, timezone
from dataclasses import dataclass, field

from src.domain.exceptions import (
    InvalidReviewBookError,
    InvalidReviewRatingError,
    InvalidReviewUserError,
)


@dataclass
class Review:
    id: int | None = field(default=None)
    rating: int = field(default=0)
    comment: str | None = field(default=None)
    isSpoiler: bool = field(default=False)
    user_id: int = field(default=0)
    book_id: int = field(default=0)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc), kw_only=True
    )

    def __post_init__(self):
        if not 1 <= self.rating <= 5:
            raise InvalidReviewRatingError(self.rating)

        if self.user_id <= 0:
            raise InvalidReviewUserError(self.user_id)

        if self.book_id <= 0:
            raise InvalidReviewBookError(self.book_id)
