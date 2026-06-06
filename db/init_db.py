import asyncio
import os
import asyncpg
from db.pool import get_conn, init_pool, close_pool
from dotenv import load_dotenv


load_dotenv()


from pathlib import Path
sql_path = Path(__file__).parent / "schema.sql"

async def init_db() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("<!!> <Failed to load database url>")
    print(f"<Initializing database...> <database_url GET>")
    sql = sql_path.read_text(encoding="utf-8")
    
    async with get_conn() as conn:
        try:
            await conn.execute(sql)
            print("<Database initialized successfully>")
        except Exception as e:
            raise Exception(f"<!!> <Failed to initialize database: {e}>")



async def test() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("<!!> <Failed to load database url>")
    await init_pool(database_url)
    await init_db()
    await close_pool()

if __name__ == "__main__":
    asyncio.run(test())