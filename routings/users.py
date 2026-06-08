from fastapi import APIRouter, HTTPException
from uuid import UUID 
from db.repos import users, chats 

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
async def create_user(): 
    uid = await users.create_user()
    if uid is None:
        raise HTTPException(status_code=500, detail="Error: Failed to create user")
    return {"user_id": uid}

@router.get("/{user_id}")
async def get_user(user_id: UUID):
    user = await users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Error: User not found")
    return user

@router.get("/{user_id}/chats")
async def get_all_titles(user_id: UUID):
    titles = await chats.get_titles(user_id)
    if not titles:
        raise HTTPException(status_code=404, detail="Error: Failed to load chat titles")
    return titles