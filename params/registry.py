from dataclasses import dataclass


@dataclass(frozen=True)
class ParamDef:
    name: str             
    label: str      # 中文名
    desc: str             
    min: float          
    max: float            
    baseline: float       
    half_life_min: float  #半衰期


REGISTRY: dict[str, ParamDef] = {
    "valence": ParamDef(
        name="valence", 
        label="心情",
        desc="当前心情好坏(负=低落/不爽,正=愉快)",
        min=-1.0, 
        max=1.0, 
        baseline=0.0, 
        half_life_min=30.0,
    ),
    "energy": ParamDef(
        name="energy", 
        label="精力",
        desc="整体精力活力(低=疲惫话少,高=精神话多)",
        min=0.0, 
        max=1.0,
        baseline=0.8, 
        half_life_min=240.0,
    ),
    "interest": ParamDef(
        name="interest", 
        label="兴趣",
        desc="对当前话题的投入(低=想敷衍/换话题,高=想追问展开)",
        min=0.0, 
        max=1.0, 
        aseline=0.5, 
        half_life_min=20.0,
    ),
}