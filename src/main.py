from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def status():
    return {"status": "healthy"}
