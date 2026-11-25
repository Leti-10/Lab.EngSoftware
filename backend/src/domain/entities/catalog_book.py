from dataclasses import dataclass, field


@dataclass
class CatalogBook:
    isbn: str
    title: str
    authors: list[str] = field(default_factory=list)
    publisher: str = ""
    genres: list[str] = field(default_factory=list)
    cover_url: str | None = None
