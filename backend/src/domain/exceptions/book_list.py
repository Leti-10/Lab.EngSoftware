from .base import DomainError


class ListNameTooShortError(DomainError):
    def __init__(self, name: str):
        super().__init__(
            f"O nome '{name}' é muito curto. Deve ter pelo menos 3 caracteres."
        )


class InvalidListOwnerError(DomainError):
    def __init__(self, reason: str):
        super().__init__(f"A lista deve ter um dono, {reason} é inválido.")


class BookListNotFoundError(DomainError):
    def __init__(self, list_id: int):
        super().__init__(f"Lista {list_id} não encontrada.")


class BookListForbiddenError(DomainError):
    def __init__(self):
        super().__init__("Você não tem permissão para alterar esta lista.")


class BookAlreadyInListError(DomainError):
    def __init__(self):
        super().__init__("Este livro já está na lista.")
