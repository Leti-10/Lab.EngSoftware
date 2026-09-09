from fastapi import FastAPI

from route.user_route import router as user_router
from controller import authController


app = FastAPI()

app.include_router(user_router)
app.include_router(authController.router)


@app.get("/")
async def status():
    return {
        "status": "healthy",
        "message": "Capivaras são demais!"
    }