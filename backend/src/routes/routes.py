from fastapi import APIRouter

from src.controller.auth_controller import router as auth_router
from src.controller.user_controller import router as user_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
