from fastapi import APIRouter, HTTPException
from uuid import UUID
from db.repos import users, chats 
from schemas.chats import CreateChatBody, Message 
from llm import service

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/")
async def create_chat(body: CreateChatBody):
    uid = body.user_id

    if not await users.exists(uid):
        raise HTTPException(status_code=404, detail="Error: User not found")

    chat_id = await chats.create_chat(user_id=uid, title=body.title)
    if chat_id is None:
        raise HTTPException(status_code=500, detail="Error: Failed to create chat")

    return {"chat_id": chat_id}



@router.get("/{chat_id}")
async def get_chat_by_id(chat_id: UUID):
    chat = await chats.get_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Error: Failed to load chat")
    return chat

@router.delete("/{chat_id}")
async def delete_chat(chat_id: UUID):
    result = await chats.delete_chat(chat_id)
    if not result:
        raise HTTPException(status_code=409, detail="Error: Failed to delete chat")

@router.post("/{chat_id}/messages")
async def send_message(chat_id: UUID, message: Message):
    if not await chats.exists(chat_id):
        raise HTTPException(status_code=404, detail="Error: Chat not found")
    
    user_prompt = {"role": "user", "content": message.content}
    await chats.add_message(chat_id, user_prompt)

    chat = await chats.get_by_id(chat_id) # 以后应该换成, 只拿最近的几份记录, 或者仅仅更新刚刚ai回答的消息
    llm_message = await service.call_llm_api(chat["messages"])
    if llm_message is None:
        raise HTTPException(500, "Error: Failed to get llm response")
    await chats.add_message(chat_id, {"role": "assistant", "content": llm_message})
    return {"role": "assistant", "content": llm_message}