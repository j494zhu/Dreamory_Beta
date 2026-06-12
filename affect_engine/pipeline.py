"""
管线编排:对应你原来 send_message 里 ①~⑨ 的部分。
关键改动:抽取在生成【之前】—— 她的回复必须反映"他刚说的这句"对状态的影响。

依赖你现有的 chats / service 模块,直接替换原 router 函数体即可。
"""
import re
import time
from uuid import UUID

from . import extractor, dynamics, injector
from .state import AffectState
from .persona import Persona, PRESETS

_REPLY_RE = re.compile(r"<reply>(.*?)</reply>", re.S)
_THINKING_RE = re.compile(r"<thinking>(.*?)</thinking>", re.S)


def _parse_generation(raw: str) -> tuple[str, str]:
    """解析两段式输出。解析失败时整体当 reply(降级而非崩溃)。"""
    reply_m = _REPLY_RE.search(raw)
    think_m = _THINKING_RE.search(raw)
    thinking = think_m.group(1).strip() if think_m else ""
    if reply_m:
        return thinking, reply_m.group(1).strip()
    # 降级:剥掉 thinking 部分,剩下的当回复
    cleaned = _THINKING_RE.sub("", raw).strip()
    return thinking, cleaned or raw.strip()


def _recent_context(messages: list[dict], n: int = 6) -> str:
    tail = messages[-n:]
    role_name = {"user": "他", "assistant": "她"}
    return "\n".join(f"{role_name.get(m['role'], m['role'])}: {m['content']}" for m in tail)


def _her_last_msg(messages: list[dict]) -> str | None:
    for m in reversed(messages):
        if m["role"] == "assistant":
            return m["content"]
    return None


async def handle_message(chat_id: UUID, user_content: str,
                         chats, service) -> dict:
    """
    chats / service 是你现有的存储与 LLM 模块。
    chats 需新增/复用三个方法:
      get_affect(chat_id) -> dict | None      存的 state.to_dict()
      set_affect(chat_id, dict)
      get_persona(chat_id) -> dict | None     没有则用 PRESETS
    """
    # ── 0. 载入 ───────────────────────────────────────────
    chat = await chats.get_by_id(chat_id)
    history = chat["messages"]

    persona_d = await chats.get_persona(chat_id)
    persona = Persona.from_dict(persona_d) if persona_d else PRESETS["anxious"]

    state_d = await chats.get_affect(chat_id)
    state = AffectState.from_dict(state_d) if state_d else AffectState.fresh(persona)

    # ── 1. 时间效应(arousal 冷却 / 会话边界 / 回路沉淀)───────
    dynamics.apply_time(state, persona, now=time.time())

    # ── 2. 事件抽取(LLM①:分类,不打分)─────────────────────
    her_last = _her_last_msg(history)
    ctx = _recent_context(history)
    events = await extractor.extract(her_last, user_content, ctx, state)

    # ── 3. 动力学更新(纯代码)────────────────────────────────
    trace = dynamics.apply_events(state, events, persona, her_last, user_content)
    trace += dynamics.transition(state, events, persona)

    # ── 4. 入库用户消息,渲染注入 ─────────────────────────────
    await chats.add_message(chat_id, {"role": "user", "content": user_content})
    system_prompt = injector.render(state, persona)
    messages = [{"role": "system", "content": system_prompt}] + history \
        + [{"role": "user", "content": user_content}]

    # ── 5. 生成(LLM②):pro 是 reasoning 模型,reasoning_content 即内心独白,content 即回复 ──
    content, reasoning = await service.generate(messages)
    if content is None:
        raise RuntimeError("Error: llm generation failed")
    fallback_think, reply = _parse_generation(content)  # 兜底:剥离可能残留的 <reply>/<thinking> 标签
    thinking = reasoning or fallback_think

    # ── 6. 落库:reply 进对话历史,thinking 和 trace 进调试日志 ──
    await chats.add_message(chat_id, {"role": "assistant", "content": reply})
    await chats.set_affect(chat_id, state.to_dict())

    return {
        "role": "assistant",
        "content": reply,
        "debug": {                      # 生产环境可以关掉,调试期是命脉
            "thinking": thinking,
            "mode": state.mode,
            "events": events,
            "trace": trace,
            "open_loops": [l.content for l in state.open_loops],
            "grievances": [g.content for g in state.grievances if not g.resolved],
            "scalars": {
                "arousal": round(state.arousal, 2),
                "security": round(state.security, 2),
                "patience": state.patience,
                "warm_streak": state.warm_streak,
            },
        },
    }
