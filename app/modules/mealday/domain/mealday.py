from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from modules.track.interface.schema.track_schema import MealTime

@dataclass
class Dish:  # 식단등록
    id: str
    user_id: str
    meal_id: str
    name: str = field(default="새로운 식단 등록")
    picture: Optional[str] = None
    text: str = field(default="내용 입력")
    record_datetime: datetime = field(default_factory=datetime.utcnow)
    update_datetime: datetime = field(default_factory=datetime.utcnow)
    heart: bool = field(default=False)
    carb: float = field(default=0.0)
    protein: float = field(default=0.0)
    fat: float = field(default=0.0)
    calorie: float = field(default=0.0)
    unit: str = field(default="gram")  ##저장단위
    size: float = field(default=0.0)  # 저장 사이즈
    track_goal: bool = field(default=False)
    label: Optional[int] = None
    trackpart_id: Optional[str] = None # 트랙참여 id
    meal: Optional["Meal"] = field(default=None)

@dataclass
class Meal: # 식사
    id: str
    mealday_id: str
    mealtime: MealTime
    check: bool = field(default=False) #완료체크
    mealday: Optional["MealDay"] = field(default=None)
    dishes: List[Dish] = field(default_factory=list)

@dataclass
class MealDay:
    id: str
    user_id: str
    record_date: date
    update_datetime: datetime
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
    meals: List[Meal] = field(default_factory=list)

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


