'''
这个测试文件需要先启动app以后才能运行
uv run -m test.test_api_flow

测试的时候会稍微卡顿一下, 因为涉及到了调用llm api
'''


import asyncio
import os
import sys
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

async def test_api_flow():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = "http://localhost:7234"

    async with AsyncClient(base_url=base_url) as client:
        # 1. 创建用户
        r = await client.post("/users/")
        print(f"POST /users/ -> {r.status_code}: {r.text}")
        user_id = r.json()["user_id"]

        # 2. 创建聊天
        r = await client.post("/chats/", json={"user_id": user_id})
        chat_id = r.json()["chat_id"]

        # 3. send first message
        r1 = await client.post(f"/chats/{chat_id}/messages", json={"content": "随机说出5个数字. 输出格式: 一行, 5个数字, 用空格隔开, 首尾不要有多余空格"})

        # 4. send second message
        r2 = await client.post(f"/chats/{chat_id}/messages", json={"content": "重复刚刚5个数字. 输出格式: 一行, 5个数字, 用空格隔开, 首尾不要有多余空格"})

        first_text = r1.json()["content"]
        second_text = r2.json()["content"]

        # 5. 独立调用 LLM 比对两轮输出
        cmp = f"第一轮: {first_text}\n第二轮: {second_text}\n请判断这两轮的5个数字是否一致, 无视顺序. 一致回复 YES, 否则回复 NO 并解释."
        llm = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        resp = await llm.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": cmp}],
            temperature=0
        )
        judge = resp.choices[0].message.content

        ok = judge is not None and "YES" in judge.upper()
        print(f"第一轮: {first_text}")
        print(f"第二轮: {second_text}")
        print(f"判断: { 'YES 一致' if ok else f'NO 不一致 - {judge}' }")

        # 6. 删除聊天
        await client.delete(f"/chats/{chat_id}")


if __name__ == "__main__":
    asyncio.run(test_api_flow())
