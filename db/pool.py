import asyncpg
import json
from contextlib import asynccontextmanager

_pool: asyncpg.Pool | None = None 


# 注册一个jsonb的编解码器
async def _init_connection(conn) -> None:
    await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


async def init_pool(url) -> None:
    global _pool 
    _pool = await asyncpg.create_pool(url, min_size=1, max_size=10, init=_init_connection)

async def close_pool() -> None:
    global _pool 
    if _pool is not None:
        await _pool.close()
        _pool = None 

@asynccontextmanager
async def get_conn():
    if _pool is None:
        raise RuntimeError("<_pool is None> <Maybe init_pool() first> <Maybe docker is not running>")
    async with _pool.acquire() as conn:
        yield conn