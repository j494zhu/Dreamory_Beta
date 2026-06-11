from datetime import datetime, timezone
from params import REGISTRY


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def default_params() -> dict:
    """全新 chat 的初始参数:全部取基线 + 当前时间戳。"""
    p: dict = {name: d.baseline for name, d in REGISTRY.items()}
    p["updated_at"] = _now().isoformat()
    return p


def ensure(params: dict | None) -> dict:
    """把 db 读出来的 params 规整成合法状态:
    空 {} → 填默认;缺参数 → 补基线;越界 → clamp;没时间戳 → 补现在。
    新加的参数会在这里自动补上(热插拔)。"""
    params = dict(params or {})
    for name, d in REGISTRY.items():
        v = params.get(name)
        if not isinstance(v, (int, float)):
            params[name] = d.baseline
        else:
            params[name] = _clamp(float(v), d.min, d.max)
    if "updated_at" not in params:
        params["updated_at"] = _now().isoformat()
    return params


def apply_decay(params: dict, now: datetime | None = None) -> dict:
    """按各参数的半衰期,把当前值向基线拉回(惯性/衰减,纯代码)。
    离上次更新越久,滑回基线越多。"""
    params = ensure(params)
    now = now or _now()
    last = datetime.fromisoformat(params["updated_at"])
    elapsed_min = max(0.0, (now - last).total_seconds() / 60.0)
    for name, d in REGISTRY.items():
        factor = 0.5 ** (elapsed_min / d.half_life_min)   # 半衰期衰减
        params[name] = _clamp(
            d.baseline + (params[name] - d.baseline) * factor, d.min, d.max
        )
    params["updated_at"] = now.isoformat()
    return params