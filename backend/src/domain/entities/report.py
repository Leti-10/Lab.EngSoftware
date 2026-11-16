from dataclasses import dataclass, field

from src.domain.exceptions import (
    InvalidReportDescriptionError,
    InvalidReportTargetError,
    InvalidReportTargetEntityError,
    InvalidReportUserError,
)


@dataclass
class Report:
    id: int | None = field(default=None)
    user_id: int = field(default=0)
    target_id: int = field(default=0)
    target_entity: str = field(default="")
    description: str = field(default="")

    def __post_init__(self):
        if self.user_id <= 0:
            raise InvalidReportUserError(self.user_id)

        if self.target_id <= 0:
            raise InvalidReportTargetError(self.target_id)

        if not self.target_entity.strip():
            raise InvalidReportTargetEntityError(self.target_entity)

        if not self.description.strip() or len(self.description) > 1000:
            raise InvalidReportDescriptionError()
