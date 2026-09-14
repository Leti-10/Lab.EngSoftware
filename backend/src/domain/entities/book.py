from dataclasses import dataclass, field


@dataclass
class Book:
    id: int = field(init=False)
    isbn: str = field(default="")
    genre: list = field(default_factory=list)
    theme: list = field(default_factory=list)
    title: str = field(default="")
    author: list = field(default_factory=list)
    publisher: str = field(default="")

    def __post_init__(self):
        if not self.isbn or len(self.isbn) < 10:
            raise ValueError("ISBN deve ter no mínimo 10 dígitos")

        if not self.title or len(self.title) < 1:
            raise ValueError("Title deve ter pelo menos 1 caracteres")

        if not self.author or len(self.author) < 1:
            raise ValueError("Author deve ter pelo menos 1 caracteres")

        if not self.publisher or len(self.publisher) < 1:
            raise ValueError("Publisher deve ter pelo menos 1 caracteres")
