from pydantic import BaseModel


class CatalogBookSchema(BaseModel):
    isbn: str
    title: str
    authors: list[str]
    publisher: str
    genres: list[str]
    cover_url: str | None
