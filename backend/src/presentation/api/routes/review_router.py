from fastapi import APIRouter, Depends, status

from src.application.use_cases.review.create_review import CreateReviewUseCase
from src.domain.entities.review import Review
from src.domain.repositories.review_repository import ReviewRepository
from src.infrastructure.persistence.repositories.inmemory_review_repository import (
    InMemoryReviewRepository,
)
from src.presentation.api.schemas.review_schema import CreateReviewSchema

router = APIRouter(prefix="/reviews", tags=["Reviews"])

in_memory_repo_instance = InMemoryReviewRepository()


def get_review_repository() -> ReviewRepository:
    return in_memory_repo_instance


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: CreateReviewSchema,
    repository: ReviewRepository = Depends(get_review_repository),
):
    try:
        use_case = CreateReviewUseCase(repository)
        new_review = await use_case.execute(Review(**payload.model_dump()))
        return new_review
    except Exception as exc:
        return exc


@router.get("/{review_id}")
async def get_review(review_id: int):
    return {"review_id": review_id}
