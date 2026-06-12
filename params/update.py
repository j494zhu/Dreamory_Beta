from params import REGISTRY
from params.state import ensure, _clamp

def apply_events(params: dict, events: list[dict]) -> dict: # 返回新的参数表
    params = ensure(params)
    if not events:
        return params
    for event in events:
        if not isinstance(event, dict):
            continue 
        name = event.get("param") # type(event) 本质上是json
        delta = event.get("delta")
        if not isinstance(delta, (int, float)):
            continue 
        if name not in REGISTRY:
            continue 
        d = REGISTRY[name]
        delta = float(delta)
        if delta >= 0:
            delta = min(delta, d.max_up)        # 上调:小步(恢复慢)
        else:
            delta = max(delta, -d.max_down)     # 下调:大步(崩得快)
        params[name] = _clamp(params[name] + delta, d.min, d.max)
    return params