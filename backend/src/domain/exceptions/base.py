class DomainError(Exception):
    """Classe base para erros do domínio do livro."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
