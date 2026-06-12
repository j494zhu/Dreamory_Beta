import json
from llm import client
from llm.client import GEN_MODEL

async def call_llm_api(messages: list[dict]) -> str | None:
    c = client.get_client()
    response = await c.chat.completions.create(
        model=GEN_MODEL,
        messages=messages,
        temperature=0.3 # 这个参数应该让用户可以自动调节. 补兑! 甚至应该可以让后台的情感分析模型来自动调节!!
    )
    finish_reason = response.choices[0].finish_reason
    llm_message = response.choices[0].message
    if finish_reason != "stop" or llm_message is None or not llm_message.content:
        print(f"Error: Failed to get llm response")
        return None
    return llm_message.content


async def generate(messages: list[dict]) -> tuple[str | None, str | None]:
    """对话生成:返回 (content, reasoning_content)。
    deepseek-v4-pro 是 reasoning 模型,reasoning_content 即原生内心独白;
    content 即实际回复。非 reasoning 模型 reasoning 为 None。"""
    c = client.get_client()
    response = await c.chat.completions.create(
        model=GEN_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=1200,
    )
    ch = response.choices[0]
    msg = ch.message
    content = msg.content or None
    reasoning = getattr(msg, "reasoning_content", None) or None
    if ch.finish_reason != "stop" or content is None:
        print(f"Error: generation failed (finish={ch.finish_reason}, content_empty={content is None})")
        return None, reasoning
    return content, reasoning  