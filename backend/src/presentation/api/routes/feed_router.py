from fastapi import APIRouter, Depends

from src.application.use_cases.social import BuildFeedUseCase
from src.domain.entities import User
from src.domain.repositories import BookRepository, UserRepository, VoteRepository
from src.domain.repositories.review_repository import ReviewRepository
from src.domain.repositories.social_repository import FollowRepository
from src.presentation.api.dependencies import (
    get_current_user,
    get_follow_repository,
    get_review_repository,
    get_user_repository,
)
from src.presentation.api.routes.book_router import get_book_m_repository
from src.presentation.api.routes.review_router import build_responses
from src.presentation.api.routes.vote_router import get_vote_repository
from src.presentation.api.schemas.social_schema import FeedItemSchema

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("")
async def get_feed(
    follows: FollowRepository = Depends(get_follow_repository),
    reviews: ReviewRepository = Depends(get_review_repository),
    users: UserRepository = Depends(get_user_repository),
    votes: VoteRepository = Depends(get_vote_repository),
    books: BookRepository = Depends(get_book_m_repository),
    current_user: User = Depends(get_current_user),
) -> list[FeedItemSchema]:
    found = await BuildFeedUseCase(follows, reviews).execute(current_user.id)
    responses = await build_responses(found, users, votes, current_user)
    items = []
    for response in responses:
        book = await books.get_by_id(response.book_id)
        items.append(
            FeedItemSchema(
                **response.model_dump(), book_title=book.title if book else None
            )
        )
    return items
