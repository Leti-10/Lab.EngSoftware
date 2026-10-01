from .base import DomainError


class InvalidVoteStatusError(DomainError):
    def __init__(self):
        super().__init__("O status do voto não pode ser vazio.")


class InvalidVoteTargetError(DomainError):
    def __init__(self, target):
        super().__init__(f"O alvo '{target}' para o voto é inválido.")


class InvalidVoteUserError(DomainError):
    def __init__(self, user_id: int):
        super().__init__(f"O usuário com ID '{user_id}' é inválido.")