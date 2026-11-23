from dataclasses import dataclass, field

from src.domain.enums.enums import EnumReadingStatus
from src.domain.exceptions import (
    InvalidReadingBookError,
    InvalidReadingStatusError,
    InvalidReadingUserError,
)


@dataclass
class Reading:
    id: int | None = field(default=None)
    user_id: int = field(default=0)
    book_id: int = field(default=0)
    status: EnumReadingStatus | str = field(default="")

    def __post_init__(self):
        if self.user_id <= 0:
            raise InvalidReadingUserError(self.user_id)

        if self.book_id <= 0:
            raise InvalidReadingBookError(self.book_id)

        if not isinstance(self.status, EnumReadingStatus):
            try:
                self.status = EnumReadingStatus(self.status)
            except ValueError:
                raise InvalidReadingStatusError(self.status) from None
