import json
from llm import client 
from llm.client import MODEL

async def call_llm_api(messages: list[dict]) -> str | None:
    c = client.get_client()
    response = await c.chat.completions.create(
        model=MODEL, 
        messages=messages, 
        temperature=0.3
    )
    finish_reason = response.choices[0].finish_reason 
    llm_message = response.choices[0].message 
    if finish_reason != "stop" or llm_message is None or not llm_message.content:
        print(f"Error: Failed to get llm response")
        return None
    return llm_message.content 