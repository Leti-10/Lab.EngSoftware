from fastapi import FastAPI

from src.routes.routes import api_router

app = FastAPI()
app.include_router(api_router)


@app.get("/")
async def status():
    return {"status": "healthy", "message": "Capivaras são demais!"}
