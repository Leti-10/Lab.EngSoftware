from .base import DomainError


class CatalogUnavailableError(DomainError):
    def __init__(self):
        super().__init__(
            "A busca de livros está indisponível no momento. Tente novamente."
        )


class CatalogQueryTooShortError(DomainError):
    def __init__(self):
        super().__init__("Digite ao menos 2 caracteres para buscar.")
