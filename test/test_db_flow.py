import asyncio 
import os
from dotenv import load_dotenv 

from db.pool import init_pool, close_pool
from db.repos import users, chats 

load_dotenv()

async def main():
    url = os.getenv("DATABASE_URL")
    await init_pool(url)

    try:
        uid = await users.create_user()
        assert uid is not None
        print(f"ok, user created: {uid}")

        chat_id = await chats.create_chat(user_id=uid, title="---testing-chat---")
        assert chat_id is not None
        print(f"ok, chat created: {chat_id}")

        msgs = [{"role": "user", "content": "hi"}]
        ok = await chats.update_entire_message(chat_id=chat_id, messages=msgs)
        assert ok is True 
        print("ok, message added to database")

        chat = await chats.get_by_id(chat_id)
        assert (chat is not None) and (chat['messages'] is not None)
        print(f"ok, messages retrieved from database: {chat['messages']}")

        deleted = await chats.delete_chat(chat_id)
        assert deleted is True 
        print(f"ok, chat is deleted")
    finally:
        await close_pool()        


if __name__ == '__main__':
    asyncio.run(main())