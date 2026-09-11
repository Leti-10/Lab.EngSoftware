from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    isbn: str
    title: str


class BookPublic(BookCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
