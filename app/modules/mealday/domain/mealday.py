from dataclasses import dataclass
from datetime import date


@dataclass
class MealDay:
    id: str
    user_id: str
    record_date: date
    water: float | None
    coffee: float | None
    alcohol: float | None
    carb: float | None
    protein: float | None
    fat: float | None
    cheating: int | None
    goalcalorie: float | None
    nowcalorie: float | None
    burncalorie: float | None
    gb_carb: str | None
    gb_protein: str | None
    gb_fat: str | None
    weight: float | None
    routine_success_rate: float | None
    track_id: str | None