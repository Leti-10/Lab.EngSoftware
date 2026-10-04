from pydantic import BaseModel, Field


class CreateBookSchema(BaseModel):
    isbn: str
    title: str
    publisher: str
    authors: list[str]
    genre: list[str]
    theme: list[str] = Field(default_factory=list)


class BookResponseSchema(BaseModel):
    id: int
    isbn: str
    title: str
    publisher: str
    authors: list[str]
    genre: list[str]
    theme: list[str]
