from .base import DomainError


class InvalidCredentialsError(DomainError):
    def __init__(self):
        super().__init__("E-mail ou senha inválidos.")
