import logging
from contextlib import asynccontextmanager

from src.infrastructure.persistence.database import get_db_context
from src.infrastructure.persistence.repositories.orm_book_repository import (
    SQLAlchemyRepository,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core import settings
from src.infrastructure.seed import seed_native_catalog
from src.presentation.api.routes import api_router

logging.basicConfig(level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.SEED_CATALOG:
        async for session in get_db_context():
            sqlalchemy_repo_instance = SQLAlchemyRepository(session)
            await seed_native_catalog(sqlalchemy_repo_instance)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Sistema de Gerenciamento de Livros",
    description="API desenvolvida seguindo DDD, SOLID e Clean Architecture",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "online", "architecture": "Clean Architecture / DDD"}
