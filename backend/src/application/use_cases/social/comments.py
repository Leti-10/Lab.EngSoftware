from src.domain.entities.social import Comment
from src.domain.exceptions.social import CommentForbiddenError, CommentNotFoundError
from src.domain.repositories.social_repository import CommentRepository


class AddCommentUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    async def execute(self, review_id: int, user_id: int, text: str) -> Comment:
        comment = Comment(review_id=review_id, user_id=user_id, text=text)
        return await self.comment_repository.save(comment)


class ListCommentsUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    async def execute(self, review_id: int) -> list[Comment]:
        return await self.comment_repository.find_by_review(review_id)


class DeleteCommentUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    async def execute(self, comment_id: int, user_id: int) -> None:
        comment = await self.comment_repository.get_by_id(comment_id)
        if comment is None:
            raise CommentNotFoundError(comment_id)
        if comment.user_id != user_id:
            raise CommentForbiddenError()
        await self.comment_repository.delete(comment_id)
