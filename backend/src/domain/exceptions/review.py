from .base import DomainError


class InvalidReviewError(DomainError):
    def __init__(self):
        super().__init__("A avaliação não pode ser nula.")


class InvalidReviewRatingError(DomainError):
    def __init__(self, rating: int):
        super().__init__(f"A nota '{rating}' deve estar entre 1 e 5.")


class InvalidReviewUserError(DomainError):
    def __init__(self, user_id: int):
        super().__init__(f"O usuário com ID '{user_id}' é inválido.")


class InvalidReviewBookError(DomainError):
    def __init__(self, book_id: int):
        super().__init__(f"O livro com ID '{book_id}' é inválido.")


class ReviewNotFoundError(DomainError):
    def __init__(self, review_id: int):
        super().__init__(f"Review {review_id} não encontrada.")
