from params import REGISTRY

def _band(value: float, lo: float, hi: float) -> str:
    """把值归一化到 0~1,再分 低/中/高 三档。"""
    if hi == lo:
        return "中"
    t = (value - lo) / (hi - lo)
    if t < 0.34:
        return "低"
    if t < 0.67:
        return "中"
    return "高"


# 每个参数 → 档位 → 对【这条回复】的硬性行为约束(命令式,不是建议)。
# "中" 档不注入(只把偏离中性的状态喂给模型,避免稀释、让低/高更突出)。
_PHRASES = {
    "valence": {
        "低": "心情差:语气冷淡、简短;不要用表情和语气词,不要主动热络、不要哄人,可以略带不耐烦或敷衍。",
        "高": "心情好:语气轻快,可以多用表情、主动调侃、热络一点。",
    },
    "energy": {
        "低": "很累:回复明显变短(最多一两句),懒得展开,不主动找话题;可能只回'嗯''困了''不想说话'。",
        "高": "精力旺:可以话多一点、更主动,愿意起新话题。",
    },
    "interest": {
        "低": "对这个话题没兴趣:只回一句,敷衍带过,不要追问、不要展开,可以冷淡或岔开话题。",
        "高": "很感兴趣:愿意追问、展开、多聊几句,表现出投入。",
    },
}


def render(param: dict) -> str:
    lines = []
    for name, d in REGISTRY.items():
        value = param.get(name, d.baseline)
        band = _band(value, d.min, d.max)
        phrase = _PHRASES.get(name, {}).get(band)   # 中档为 None → 跳过
        if phrase:
            lines.append(f"- {phrase}")

    if not lines:
        state_block = "- 状态平稳,正常发挥即可。"
    else:
        state_block = "\n".join(lines)

    return (
        "【你此刻的内在状态 → 对这条回复的硬性要求】\n"
        "下面是你此刻真实的心理/生理状态对你【这一条回复】的强制要求,"
        "必须遵守——尤其是回复的长度和语气要随之改变。\n"
        "状态差的时候,就要真的回得短、回得冷、回得敷衍,不要还像没事人一样热情周到。\n"
        "但绝对不要说出、承认或解释这些状态本身。\n"
        f"{state_block}\n"
        "(示例:兴趣低+心情差时,'今天加班好累' 这种话你可能就回一句 '哦,辛苦' 就完了,不展开。)"
    )
