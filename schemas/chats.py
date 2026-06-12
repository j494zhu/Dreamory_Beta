from pydantic import BaseModel 
from uuid import UUID

class CreateChatBody(BaseModel):
    user_id: UUID
    title: str | None = None

class Message(BaseModel):
    content: str

class PersonaBody(BaseModel):
    preset: str | None = None      # secure / anxious / avoidant;非法或 None → 用默认 Persona
    name: str | None = None        # 留空则沿用预设默认名字
    profile: str | None = None     # 留空则沿用预设默认简介