from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from modules.track.interface.schema.track_schema import MealTime

@dataclass
class MealHour:  # 식단등록(Hour)
    id: str
    user_id: str
    daymeal_id: str
    meal_time: MealTime
    name: str = field(default="새로운 식단 등록")
    picture: Optional[str] = None
    text: str = field(default="내용 입력")
    record_datetime: datetime = field(default_factory=datetime.utcnow)
    heart: bool = field(default=False)
    carb: float = field(default=0.0)
    protein: float = field(default=0.0)
    fat: float = field(default=0.0)
    calorie: float = field(default=0.0)
    unit: str = field(default="gram")  ##저장단위
    size: float = field(default=0.0)  # 저장 사이즈
    track_goal: bool = field(default=False)  # Track에 맞게 지켰는지 여부
    label: Optional[int] = None
    mealday: Optional["MealDay"] = field(default=None)  # ✅ 기본값 추가

@dataclass
class MealDay:
    id: str
    user_id: str
    record_date: date
    water: float = field(default=0.0)
    coffee: float = field(default=0.0)
    alcohol: float = field(default=0.0)
    carb: float = field(default=0.0)
    protein: float = field(default=0.0)
    fat: float = field(default=0.0)
    cheating: int = field(default=0)
    goalcalorie: float = field(default=0.0)
    nowcalorie: float = field(default=0.0)
    burncalorie: float = field(default=0.0)
    gb_carb: Optional[str] = None
    gb_protein: Optional[str] = None
    gb_fat: Optional[str] = None
    weight: float = field(default=0.0)
    routine_success_rate: float = field(default=0.0)
    track_id: Optional[str] = None

    # 관계 매핑을 위한 필드
    mealhours: List[MealHour] = field(default_factory=list)

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


