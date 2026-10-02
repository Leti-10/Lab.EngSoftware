from pydantic import BaseModel

from .book_schema import BookResponseSchema


class CreateBookListSchema(BaseModel):
    name: str
    description: str
    private: bool = False


class AddBookToListSchema(BaseModel):
    book_id: int


class BookListResponseSchema(BaseModel):
    id: int
    owner: int
    name: str
    description: str
    private: bool
    books: list[BookResponseSchema]
