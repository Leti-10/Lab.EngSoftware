from fastapi import APIRouter, Depends

from src.application.use_cases.social import RecommendBooksUseCase
from src.domain.entities import User
from src.domain.repositories import BookRepository, ReadingRepository
from src.domain.repositories.review_repository import ReviewRepository
from src.presentation.api.dependencies import get_current_user, get_review_repository
from src.presentation.api.routes.book_router import get_book_repository, to_response
from src.presentation.api.routes.reading_router import get_reading_repository
from src.presentation.api.schemas.social_schema import RecommendationSchema

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("")
async def get_recommendations(
    reviews: ReviewRepository = Depends(get_review_repository),
    readings: ReadingRepository = Depends(get_reading_repository),
    books: BookRepository = Depends(get_book_repository),
    current_user: User = Depends(get_current_user),
) -> list[RecommendationSchema]:
    found = await RecommendBooksUseCase(reviews, readings, books).execute(
        current_user.id
    )
    return [
        RecommendationSchema(book=to_response(item.book), reason=item.reason)
        for item in found
    ]
