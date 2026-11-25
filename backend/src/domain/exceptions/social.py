from .base import DomainError


class InvalidCommentError(DomainError):
    pass


class CommentNotFoundError(DomainError):
    def __init__(self, comment_id: int):
        super().__init__(f"Comentário {comment_id} não encontrado.")


class InvalidFollowError(DomainError):
    pass


class CommentForbiddenError(DomainError):
    def __init__(self):
        super().__init__("Você só pode apagar o seu próprio comentário.")
