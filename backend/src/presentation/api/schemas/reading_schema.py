from pydantic import BaseModel, ConfigDict

from src.domain.enums.enums import EnumReadingStatus


class SetReadingSchema(BaseModel):
    status: EnumReadingStatus


class ReadingResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    book_id: int
    status: EnumReadingStatus
