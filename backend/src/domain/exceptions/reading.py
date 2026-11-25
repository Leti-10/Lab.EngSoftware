from .base import DomainError


class InvalidReadingStatusError(DomainError):
    def __init__(self, status):
        super().__init__(f"O status de leitura '{status}' é inválido.")


class InvalidReadingUserError(DomainError):
    def __init__(self, user_id: int):
        super().__init__(f"O usuário com ID '{user_id}' é inválido.")


class InvalidReadingBookError(DomainError):
    def __init__(self, book_id: int):
        super().__init__(f"O livro com ID '{book_id}' é inválido.")
