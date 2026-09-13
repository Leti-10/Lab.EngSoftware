from dataclasses import dataclass

@dataclass
class Book:
    id: int
    title: str
    isbn: str
    year: int