import asyncio
from db.pool import init_pool, close_pool, get_conn 
from db.init_db import init_db
from db.repos import users, chats, archives
from llm import service
from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
database_url = os.getenv("DATABASE_URL")

from contextlib import asynccontextmanager
from schemas.chats import CreateChatBody, Message
from uuid import UUID

@asynccontextmanager
async def start_app(app: FastAPI):
    print("Hello from dreamory-beta!")
    await init_pool(database_url)
    await init_db()
    yield 
    await close_pool()
app = FastAPI(lifespan=start_app)


# --- routings ---
@app.post("/users")
async def create_user(): 
    uid = await users.create_user()
    if uid is None:
        raise HTTPException(status_code=500, detail="Error: Failed to create user")
    return {"user_id": uid}

@app.get("/users/{user_id}")
async def get_user(user_id: UUID):
    user = await users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Error: User not found")

    return user

@app.post("/chats")
async def create_chat(body: CreateChatBody):
    uid = body.user_id

    if not await users.exists(uid):
        raise HTTPException(status_code=404, detail="Error: User not found")

    chat_id = await chats.create_chat(user_id=uid, title=body.title)
    if chat_id is None:
        raise HTTPException(status_code=500, detail="Error: Failed to create chat")

    return {"chat_id": chat_id}

@app.get("/users/{user_id}/chats")
async def get_all_titles(user_id: UUID):
    titles = await chats.get_titles(user_id)
    if not titles:
        raise HTTPException(status_code=404, detail="Error: Failed to load chat titles")
    return titles

@app.get("/chats/{chat_id}")
async def get_chat_by_id(chat_id: UUID):
    chat = await chats.get_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Error: Failed to load chat")
    return chat

@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: UUID):
    result = await chats.delete_chat(chat_id)
    if not result:
        raise HTTPException(status_code=409, detail="Error: Failed to delete chat")

@app.post("/chats/{chat_id}/messages")
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

    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7234)
    # 像这里如果有__name__=="__main__"的话, 可以直接 python main.py / uv run main.py
    # 如果没有这个模块, 那就直接uvicorn main:app --reload
