from datetime import datetime, date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, Field
from pydantic_core.core_schema import FieldValidationInfo


class CreateMealDayBody(BaseModel):
    id: Optional[str] = Field(default=None, description="ID, 입력 불필요")  #자동 증가용
    user_id: str = Field(min_length=1, max_length=50, description="User id")
    record_date: date = Field(description="기록 날짜")
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
    track_id: Optional[int] = Field(default=None, description="Track ID, 해당일 Track 여부")

class MealDayResponse_date(BaseModel):
    record_date: date