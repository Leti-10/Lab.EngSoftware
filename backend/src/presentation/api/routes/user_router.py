from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/", status_code=201)
async def create_book():
    return {"message": "Criar conta"}


@router.get("/{user_id}")
async def get_book(user_id: int):
    return {"user": user_id}
