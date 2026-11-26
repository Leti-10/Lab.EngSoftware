from fastapi import APIRouter

from src.presentation.api.routes import (
    auth_router,
    book_list_router,
    book_router,
    comment_router,
    feed_router,
    follow_router,
    notification_router,
    reading_router,
    recommendation_router,
    report_router,
    review_router,
    user_router,
    vote_router,
    catalog_router,
)

api_router = APIRouter()

api_router.include_router(auth_router.router)
api_router.include_router(book_router.router)
api_router.include_router(review_router.router)
api_router.include_router(report_router.router)
api_router.include_router(reading_router.router)
api_router.include_router(book_list_router.router)
api_router.include_router(vote_router.router)
api_router.include_router(catalog_router.router)
api_router.include_router(comment_router.router)
api_router.include_router(follow_router.router)
api_router.include_router(user_router.router)
api_router.include_router(notification_router.router)
api_router.include_router(feed_router.router)
api_router.include_router(recommendation_router.router)
