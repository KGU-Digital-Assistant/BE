from dataclasses import dataclass, field
from typing import List

from app.modules.track.domain.track_routine_food import RoutineFood


@dataclass
class Food:
    label: int
    name: str = field(default="음식이름")
    size: float = field(default=0.0)  # 저장 사이즈
    calorie: float = field(default=0.0)
    carb: float = field(default=0.0)
    sugar: float = field(default=0.0)
    fat: float = field(default=0.0)
    protein: float = field(default=0.0)
    calcium: float = field(default=0.0)
    phosphorus: float = field(default=0.0)
    sodium: float = field(default=0.0)
    potassium: float = field(default=0.0)
    magnesium: float = field(default=0.0)
    iron: float = field(default=0.0)
    zinc: float = field(default=0.0)
    cholesterol: float = field(default=0.0)
    trans_fat: float = field(default=0.0)
    image_url: str = field(default="사진경로")

    routine_foods: List[RoutineFood] = field(default_factory=list)