from src.domain.exceptions.base import DomainError


class InvalidReportUserError(DomainError):
    def __init__(self, user_id: int):
        super().__init__(f"O usuário com ID '{user_id}' é inválido.")


class InvalidReportTargetError(DomainError):
    def __init__(self, target_id: int):
        super().__init__(f"O alvo com ID '{target_id}' é inválido.")


class InvalidReportTargetEntityError(DomainError):
    def __init__(self, target_entity: str):
        super().__init__(f"A entidade do alvo '{target_entity}' é inválida.")


class InvalidReportDescriptionError(DomainError):
    def __init__(self):
        super().__init__("A descrição da denúncia deve ter entre 1 e 1000 caracteres.")
