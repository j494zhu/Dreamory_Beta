from dataclasses import dataclass 

@dataclass(frozen=True)
class ParamDef:
    name: str # eng key name
    label: str # mandarin name for prompt injection
    desc: str 
    min: float 
    max: float 
    baseline: float 
    half_life_min: float # 半衰期
    max_up: float        # 单次最大上调
    max_down: float      # 单次最大下调(通常 > max_up:情绪/信任崩得快、恢复慢)

REGISTRY: dict[str, ParamDef] = {
    "valence": ParamDef(
        name="valence",
        label="心情",
        desc="当前心情好坏(负=低落/不爽,正=愉快)",
        min=-1.0,
        max=1.0,
        baseline=0.0, # 晚点看看是否需要设立一个更高的基准
        half_life_min=30.0,
        max_up=0.10,
        max_down=0.25
    ),
    "energy": ParamDef(
        name="energy",
        label="精力",
        desc="整体精力活力(低=疲惫话少,高=精神话多)",
        min=0.0,
        max=1.0,
        baseline=0.7,
        half_life_min=120.0,
        max_up=0.05,
        max_down=0.12
    ),
    "interest": ParamDef(
        name="interest",
        label="兴趣",
        desc="对当前话题的投入(低=想敷衍/换话题,高=想追问展开)",
        min=0.0,
        max=1.0,
        baseline=0.5,
        half_life_min=20.0,
        max_up=0.15,
        max_down=0.20
    )
}

# 这几个参数是否应该相互联动? 例如 valence很高的时候不应该energy很低
# 以及要拆解每一个参数的对应特征 
# 当时他说去查询的是不是 "模仿 or 成为?"

# 以及后续要完善每一个数值到底对应什么
# 而不是直接将裸参数传给llm, 那样子肯定会表现不统一然后失真的

# 