'''
create table if not exists chats (
    chat_id uuid primary key, 
    user_id uuid not null, 
    title varchar(255), 
    messages jsonb not null default '[]'::jsonb, 
    last_used timestamptz not null default now(),
    last_compressed timestamptz
); 
'''

import uuid
from uuid import UUID
from db.pool import get_conn


async def create_chat(user_id: UUID, title: str | None = None) -> UUID | None:
    chat_id = uuid.uuid4()
    sql = "insert into chats (chat_id, user_id, title) values ($1, $2, $3) returning chat_id"
    async with get_conn() as conn:
        row = await conn.fetchrow(sql, chat_id, user_id, title)
        if row is None:
            print(f"<!!> <Error: Failed to create chat>")
            return None 
        return chat_id

async def delete_chat(chat_id: UUID) -> bool:
    sql = "delete from chats where chat_id = $1 returning chat_id"
    async with get_conn() as conn:
        result = await conn.fetchrow(sql, chat_id)
        if result is None:
            print(f"Error when deleting chat. Maybe chat_id does NOT exist")
            return False
        return True

async def update_last_used(chat_id: UUID) -> bool:
    sql = "update chats set last_used = now() where chat_id = $1 returning chat_id"
    async with get_conn() as conn:
        result = await conn.fetchrow(sql, chat_id)
        if result is None:
            print(f"<!!> <Error when updating last_compressed time of the chat>")
            return False
        return True

async def get_by_id(chat_id: UUID) -> dict | None:
    sql = "select chat_id, user_id, title, messages, last_used, last_compressed from chats where chat_id = $1"
    async with get_conn() as conn:
        result = await conn.fetchrow(sql, chat_id)
        if result is None:
            print(f"<!!> <Error when fetching row from database chats>")
            return None 
        return dict(result)

async def get_by_userid(uid: UUID) -> list[dict] | None:
    sql = "select chat_id, user_id, title, messages, last_used, last_compressed from chats where user_id = $1"
    try:
        async with get_conn() as conn:
            rows = await conn.fetch(sql, uid)
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error while fetching user's chats, user_id={uid}: {e}")
        return None

async def get_titles(uid: UUID) -> list[str | None] | None:
    sql = "select title from chats where user_id = $1"
    try:
        async with get_conn() as conn:
            titles = await conn.fetch(sql, uid)
            return [row["title"] for row in titles]
    except Exception as e:
        print(f"Error while fetching all chat tiles, {e}")
        return None

async def update_title(chat_id: UUID, title: str) -> bool:
    if len(title) > 255:
        print(f"Error: Unable to update title: title exceeds length limit 255")
        return False
    sql = "update chats set title = $1 where chat_id = $2 returning chat_id"
    async with get_conn() as conn:
        result = await conn.fetchrow(sql, title, chat_id)
        if result is None:
            print(f"Error: Unable to update title")
            return False 
        return True

async def update_entire_message(chat_id: UUID, messages: list) -> bool:
    sql = "update chats set messages = $1 where chat_id = $2 returning chat_id"
    async with get_conn() as conn:
        result = await conn.fetchrow(sql, messages, chat_id)
        if result is None:
            print(f"Error: Unable to update messages in chats")
            return False
        return True

async def add_message(chat_id: UUID, message: dict) -> bool: # pool.py已经挂上了jsonb自动编码器
    sql = "update chats set messages = messages || $1::jsonb where chat_id = $2 returning chat_id"
    async with get_conn() as conn:
        result = await conn.fetchrow(sql, message, chat_id)
        if result is None:
            print(f"Error: Unable to add message to chat messages")
            return False
        return True

async def exists(chat_id: UUID) -> bool:
    sql = "select exists(select 1 from chats where chat_id = $1)"
    async with get_conn() as conn:
        chat_exists = await conn.fetchval(sql, chat_id)
        return chat_exists
