from .base import DomainError


class ReportDescriptionTooShortError(DomainError):
    def __init__(self):
        super().__init__(
            f"Essa descrição é muito rasa. Deve ter pelo menos 10 caracteres."
        )

class InvalidReportTargetError(DomainError):
    def __init__(self, target):
        super().__init__(
            f"O alvo {target} para o report é inválido."
        )