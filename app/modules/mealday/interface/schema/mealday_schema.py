from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field
from modules.track.interface.schema.track_schema import MealTime

class CreateMealDayBody(BaseModel):
    id: Optional[str] = Field(default=None, description="ID, 입력 불필요")  #자동 증가용
    user_id: str = Field(min_length=1, max_length=50, description="User id")
    record_date: date = Field(description="기록 날짜")
    update_datetime: datetime = Field(default=datetime.utcnow(), description="기록시간")
    water: Optional[float] = Field(default=0.0, ge=0, description="섭취한 물(잔)")
    coffee: Optional[float] = Field(default=0.0, ge=0, description="섭취한 커피(잔)")
    alcohol: Optional[float] = Field(default=0.0, ge=0, description="섭취한 알코올(잔)")
    carb: Optional[float] = Field(default=0.0, ge=0, description="탄수화물 섭취량(g)")
    protein: Optional[float] = Field(default=0.0, ge=0, description="단백질 섭취량(g)")
    fat: Optional[float] = Field(default=0.0, ge=0, description="지방 섭취량(g)")
    cheating: Optional[int] = Field(default=0, ge=0, le=2, description="치팅여부  (0~1)")
    goalcalorie: Optional[float] = Field(default=0.0, ge=0, description="목표 칼로리")
    nowcalorie: Optional[float] = Field(default=0.0, ge=0, description="현 섭취 칼로리")
    burncalorie: Optional[float] = Field(default=0.0, ge=0, description="소모 칼로리")
    gb_carb: Optional[str] = Field(default=None, max_length=10, description="탄수화물 유형")
    gb_protein: Optional[str] = Field(default=None, max_length=10, description="단백질 유형")
    gb_fat: Optional[str] = Field(default=None, max_length=10, description="지방 유형")
    weight: Optional[float] = Field(default=0.0, ge=0, description="금일 몸무게(kg)")
    routine_success_rate: Optional[float] = Field(default=None, ge=0, le=100, description="루틴 성공률(%)")
    track_id: Optional[str] = Field(default=None, description="Track ID, 해당일 Track 여부")

class MealDayResponse_Date(BaseModel):
    user_id: str
    record_date: date

class MealDayResponse_Full(BaseModel):
    id: str
    user_id: str
    record_date: date
    update_datetime: datetime
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


class UpdateMealDayBody(BaseModel):
    weight: Optional[float] = None
    burncalorie: Optional[float] = None
    water: Optional[float] = None
    coffee: Optional[float] = None
    alcohol: Optional[float] = None

########################################################################
############## Dish & Meal ##################################################
########################################################################


class UpdateDishBody(BaseModel):
    heart: Optional[bool] = None
    track_goal: Optional[bool] = None
    size: Optional[float] = None


class Dish_Full(BaseModel):
    id: str
    user_id: str
    meal_id: str
    name: Optional[str] = None
    picture: Optional[str] = None
    text: Optional[str] = None
    record_datetime: datetime
    update_datetime: datetime
    heart: Optional[bool] = None
    carb: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    calorie: Optional[float] = None
    unit: Optional[str] = None
    size: Optional[float] = None
    track_goal: Optional[bool] = None
    label: Optional[int] = None
    trackpart_id: Optional[str] = None
    class Config:
        from_attributes = True

class Dish_with_datetime(BaseModel):
    record_date: date
    mealtime: MealTime
    dish_list: List[Dish_Full]