from fastapi import APIRouter, HTTPException, Body
from uuid import UUID
from db.repos import users, chats
from schemas.chats import CreateChatBody, Message, PersonaBody
from llm import service
from affect_engine.pipeline import handle_message
from affect_engine.persona import Persona, PRESETS

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("/presets")
async def list_presets():
    """返回所有预设人格 {key: persona dict},供前端选择与预填。"""
    return {key: p.to_dict() for key, p in PRESETS.items()}


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

@router.put("/{chat_id}/persona")
async def set_persona(chat_id: UUID, body: PersonaBody):
    """设置某个 chat 的人格:取预设为底,用 name/profile 覆盖。下一条消息即生效。"""
    if not await chats.exists(chat_id):
        raise HTTPException(status_code=404, detail="Error: Chat not found")
    base = PRESETS[body.preset] if body.preset in PRESETS else Persona()
    d = base.to_dict()
    d["preset"] = body.preset if body.preset in PRESETS else None  # 记下来源,供前端回显(from_dict 会忽略此键)
    if body.name:
        d["name"] = body.name
    if body.profile:
        d["profile"] = body.profile
    if not await chats.set_persona(chat_id, d):
        raise HTTPException(status_code=500, detail="Error: Failed to set persona")
    return d


@router.put("/{chat_id}/title")
async def rename_chat(chat_id: UUID, title: str = Body(..., embed=True)):
    """重命名对话"""
    title = title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Error: title is required")
    if not await chats.update_title(chat_id, title):
        raise HTTPException(status_code=500, detail="Error: Failed to rename chat")
    return {"ok": True}


@router.delete("/{chat_id}")
async def delete_chat(chat_id: UUID):
    result = await chats.delete_chat(chat_id)
    if not result:
        raise HTTPException(status_code=409, detail="Error: Failed to delete chat")

@router.post("/{chat_id}/messages")
async def send_message(chat_id: UUID, message: Message):
    if not await chats.exists(chat_id):
        raise HTTPException(status_code=404, detail="Error: Chat not found")

    # affect_engine:抽取在生成之前 → 纯代码动力学 → 注入 → 两段式生成。
    # 返回含 debug 字段(mode / thinking / trace / open_loops / scalars)。
    try:
        return await handle_message(chat_id, message.content, chats, service)
    except Exception as e:
        raise HTTPException(500, f"Error: Failed to handle message: {e}")