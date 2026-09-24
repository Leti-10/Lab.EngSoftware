from .base import DomainError


class BookTitleTooShortError(DomainError):
    def __init__(self, title: str):
        super().__init__(
            f"O título '{title}' é muito curto. Deve ter pelo menos 3 caracteres."
        )


class BookAlreadyPublishedError(DomainError):
    def __init__(self, book_id: str):
        super().__init__(
            f"O livro com ID {book_id} já foi publicado e não pode ser editado."
        )


class InvalidISBNError(DomainError):
    def __init__(self, isbn: str):
        super().__init__(f"O código ISBN '{isbn}' informado é inválido.")
