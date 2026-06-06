import asyncio
from db.pool import init_pool, close_pool, get_conn 

import dotenv
from dotenv import load_dotenv
load_dotenv()
import os


database_url = os.getenv("DATABASE_URL")

async def test_db_connection(): 
    print("<start testing>")
    await init_pool(database_url)
    print("db init complete")
    async with get_conn() as conn:
        x = await conn.execute("select 1 as test")
        print(f"<conn test1 complete: {x}>")
        t = await conn.fetchval("select now()")
        print(f"<conn test2 complete: current_time={t}>")
        print(f"conn closed. queries done")
    await close_pool()
    print(f"pool closed")




def main():
    print("Hello from dreamory-beta!")


if __name__ == "__main__":
    main()
    asyncio.run(test_db_connection())
