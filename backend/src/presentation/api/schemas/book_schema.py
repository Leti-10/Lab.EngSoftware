from pydantic import BaseModel

class CreateBookSchema(BaseModel):
    isbn: str
    title: str
    publisher: str
    authors: list[str]
    genre: list[str]
