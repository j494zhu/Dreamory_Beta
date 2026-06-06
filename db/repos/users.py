'''
create table if not exists users (
    user_id uuid primary key, 
    created_at timestamptz not null default now()
);
'''

import uuid
from uuid import UUID
from db.pool import init_pool, close_pool, get_conn 

async def create_user() -> UUID | None:
    uid = uuid.uuid4()
    sql = "insert into users (user_id) values ($1)"
    try:
        async with get_conn() as conn:
            await conn.execute(sql, uid)
        return uid 
    except Exception as e:
        print(f"<!!> <Error: Unable to create new user>: {e}")
        return None
    # 对于重复出现的用户名, 这里应该直接返回某个特殊的错误, 这样可以提示wrong user name

async def get_by_id(uid: UUID) -> dict | None:
    sql = "select user_id, created_at from users where user_id = $1"
    async with get_conn() as conn:
        row = await conn.fetchrow(sql, uid)
        if not row:
            print(f"<Error: User not found>")
            return None
        return dict(row)

async def delete(uid: UUID) -> bool:
    sql = "delete from users where user_id = $1 returning user_id"
    async with get_conn() as conn:
        tmp = await conn.fetchrow(sql, uid)
        return tmp is not None

async def exists(uid: UUID) -> bool:
    sql = "select exists(select 1 from users where user_id = $1)"
    async with get_conn() as conn:
        uid_exists = await conn.fetchval(sql, uid)
        return uid_exists