from .base import DomainError


class ListNameTooShortError(DomainError):
    def __init__(self, name: str):
        super().__init__(
            f"O nome '{name}' é muito curto. Deve ter pelo menos 3 caracteres."
        )


class InvalidListOwnerError(DomainError):
    def __init__(self):
        super().__init__("A lista deve ter um dono.")
