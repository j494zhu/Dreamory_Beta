import json
from llm import client 
from llm.client import MODEL 
from params import REGISTRY 


def _param_catalog() -> str:
    lines = []
    for name, d in REGISTRY.items():
        lines.append(f"- {name}({d.label}):{d.desc},范围[{d.min}, {d.max}]")
    return "\n".join(lines)


def _build_message(user_msg: str, assistant_reply: str, params: dict) -> list[dict]:
    catalog = _param_catalog()
    current = ", ".join(f"{n}={params.get(n)}" for n in REGISTRY)# ??
    system_prompt = (
        "你是一个情绪状态分析器,负责观察一轮对话后,判断 AI 角色的内在参数应该如何变化。\n"
        "可调参数:\n"
        f"{catalog}\n\n"
        "规则:\n"
        "- 只为确实被明显触发的参数产出事件;没有明显变化的参数不要出现。\n"
        "- delta 是这一轮的增量/变化量(不是目标值);保持克制,通常 0.05~0.3,强烈事件才更大。\n"
        "- 方向符合常识:被夸/愉快话题→valence 升;话题重复无聊→interest 降;长对话/深夜→energy 降。\n"
        '- 严格只输出 JSON:{"events": [{"param": "valence", "delta": 0.2, "reason": "被用户夸了"}]}\n'
        '- 没有任何变化时输出 {"events": []}。'
    )
    # 后期这里应该写一个更加完善的rubric标准
    # 以及这里是否应该给出一个schema格式? 就像llm1联系项目里的那样?
    # 是否要添加一个错误重试机制? 
    user_prompt = (
        f"AI 当前参数:{current}\n\n"
        f"【用户最后一条消息】\n{user_msg}\n\n"
        f"【AI 的回复】\n{assistant_reply}\n\n"
        "请输出参数变化事件的 JSON。"
    )
    return [
        {"role": "system", "content": system_prompt}, 
        {"role": "user", "content": user_prompt}
    ]

async def extract(user_msg, assistant_reply, params: dict) -> list[dict]:
    messages = _build_message(user_msg, assistant_reply, params)
    c = client.get_client() 
    try:
        response = await c.chat.completions.create(
            model=MODEL, 
            messages=messages, 
            temperature=0.0, 
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content 
        if not content:
            return [] 
        data = json.loads(content)
        events = data.get("events", [])
        return events if isinstance(events, list) else []
    except Exception as e:
        print(f"Error: failed to extract: {e}")
        return []