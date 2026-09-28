from fastapi import FastAPI
from src.presentation.api.routes import api_router

app = FastAPI(
    title="Sistema de Gerenciamento de Livros",
    description="API desenvolvida seguindo DDD, SOLID e Clean Architecture",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "online", "architecture": "Clean Architecture / DDD"}
