import asyncio
from contextlib import asynccontextmanager
from db.pool import init_pool, close_pool, get_conn 
from db.init_db import init_db
from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv()
database_url = os.getenv("DATABASE_URL")


from routings.users import router as users_router
from routings.chats import router as chats_router


@asynccontextmanager
async def start_app(app: FastAPI):
    print("Hello from dreamory-beta!")
    await init_pool(database_url)
    await init_db()
    yield 
    await close_pool()
app = FastAPI(lifespan=start_app)


app.include_router(users_router)
app.include_router(chats_router)


if __name__ == "__main__":
    import uvicorn
    print(f"FastAPI doc is available at: http://localhost:7234/docs")
    uvicorn.run(app, host="0.0.0.0", port=7234)
    print(f"FastAPI service was terminated. ")
    # 像这里如果有__name__=="__main__"的话, 可以直接 python main.py / uv run main.py
    # 如果没有这个模块, 那就直接uvicorn main:app --reload
