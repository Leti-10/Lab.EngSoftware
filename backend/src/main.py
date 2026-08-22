from fastapi import FastAPI
from controller import userController, authController

app = FastAPI()
app.include_router(authController.router)
app.include_router(userController.router)


@app.get("/")
async def status():
    return {"status": "healthy", "message": "Capivaras são demais!"}
