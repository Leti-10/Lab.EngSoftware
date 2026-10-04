from fastapi import APIRouter

from src.presentation.api.routes import book_router, review_router

api_router = APIRouter()

api_router.include_router(book_router.router)
api_router.include_router(review_router.router)
