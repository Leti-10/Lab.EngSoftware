from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.review import (
    CreateReviewUseCase,
    FilterReviewsUseCase,
    GetReviewByIdUseCase,
    UpdateReviewUseCase,
)
from src.domain.entities.review import Review
from src.domain.exceptions import ReviewNotFoundError
from src.domain.repositories.review_repository import ReviewRepository
from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories import SQLAlchemyReviewRepository
from src.presentation.api.schemas.review_schema import (
    CreateReviewSchema,
    ReviewResponseSchema,
    UpdateReviewSchema,
    UpdateReviewSpoilerSchema,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


async def get_review_repository(
    session: AsyncSession = Depends(get_db_context),
) -> ReviewRepository:
    return SQLAlchemyReviewRepository(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: CreateReviewSchema,
    repository: ReviewRepository = Depends(get_review_repository),
) -> ReviewResponseSchema:
    try:
        use_case = CreateReviewUseCase(repository)
        new_review = await use_case.execute(Review(**payload.model_dump()))
        return ReviewResponseSchema.model_validate(new_review)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O usuário ou o livro informado não existe.",
        ) from exc


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    repository: ReviewRepository = Depends(get_review_repository),
) -> ReviewResponseSchema:
    try:
        review = await GetReviewByIdUseCase(repository).execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc
    return ReviewResponseSchema.model_validate(review)


@router.put("/{review_id}")
async def update_review(
    review_id: int,
    payload: UpdateReviewSchema,
    repository: ReviewRepository = Depends(get_review_repository),
) -> ReviewResponseSchema:
    try:
        review = await GetReviewByIdUseCase(repository).execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc

    updated_review = Review(
        id=review_id,
        rating=payload.rating,
        comment=payload.comment,
        isSpoiler=payload.isSpoiler,
        user_id=review.user_id,
        book_id=review.book_id,
    )
    try:
        updated = await UpdateReviewUseCase(repository).execute(
            review_id, updated_review
        )
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O usuário ou o livro informado não existe.",
        ) from exc
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review não encontrada."
        )
    return ReviewResponseSchema.model_validate(updated)


@router.patch("/{review_id}/spoiler")
async def update_review_spoiler(
    review_id: int,
    payload: UpdateReviewSpoilerSchema,
    repository: ReviewRepository = Depends(get_review_repository),
) -> ReviewResponseSchema:
    try:
        review = await GetReviewByIdUseCase(repository).execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc

    review.isSpoiler = payload.isSpoiler
    try:
        updated = await UpdateReviewUseCase(repository).execute(review_id, review)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from exc
    return ReviewResponseSchema.model_validate(updated)


@router.get("", response_model=list[ReviewResponseSchema])
async def filter_reviews(
    rating: int | None = Query(default=None, ge=1, le=5),
    username: str | None = Query(default=None, min_length=1),
    book_title: str | None = Query(default=None, min_length=1),
    comment: str | None = None,
    repository: ReviewRepository = Depends(get_review_repository),
) -> list[ReviewResponseSchema]:
    reviews = await FilterReviewsUseCase(repository).execute(
        rating=rating,
        username=username,
        book_title=book_title,
        comment=comment,
    )
    return [ReviewResponseSchema.model_validate(review) for review in reviews]
