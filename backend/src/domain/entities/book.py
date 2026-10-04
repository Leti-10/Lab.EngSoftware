from dataclasses import dataclass, field


@dataclass
class Book:
    id: int | None = field(default=None)
    isbn: str = field(default="")
    genre: list = field(default_factory=list)
    theme: list = field(default_factory=list)
    title: str = field(default="")
    authors: str | list = field(default="unknown")
    publisher: str = field(default="")

    def __post_init__(self):
        if not self.isbn or len(self.isbn) < 10:
            raise ValueError("ISBN deve ter no mínimo 10 dígitos")

        if not self.title or len(self.title) < 1:
            raise ValueError("Title deve ter pelo menos 1 caracteres")

        if not self.authors or len(self.authors) < 1:  # TODO: ajustar essa regra
            raise ValueError("Author deve ter pelo menos 1 caracteres")

        if not self.publisher or len(self.publisher) < 1:
            raise ValueError("Publisher deve ter pelo menos 1 caracteres")

        if self.genre is not None:
            valid = []
            for g in self.genre:
                if g.strip() != "":
                    valid.append(g)
            self.genre = valid


if __name__ == "__main__":
    book = Book(
        isbn="12300098701",
        title="A",
        publisher="noname",
        genre=["", "comédia"],
        theme=["A busca pelo saber", "auto-ajuda"],
    )
    print(book)
