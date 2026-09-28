from fastapi import APIRouter

from src.presentation.api.routes import book_router

api_router = APIRouter()

api_router.include_router(book_router.router)
