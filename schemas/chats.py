from pydantic import BaseModel 
from uuid import UUID

class CreateChatBody(BaseModel):
    user_id: UUID
    title: str | None = None

class Message(BaseModel):
    content: str