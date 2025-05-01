from datetime import datetime, date, time, timedelta
from typing import Optional, ClassVar, List

from pydantic import BaseModel, field_validator
from enum import Enum

from app.modules.user.interface.schema.user_schema import UserResponse


class MealTime(Enum):
    BREAKFAST = 'BREAKFAST'
    BRUNCH = 'BRUNCH'  #아점
    LUNCH = 'LUNCH'
    LINNER = 'LINNER'  #점저
    DINNER = 'DINNER'
    SNACK = 'SNACK'  # 간식


class FlagStatus(Enum):
    READY = "READY"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"


class DateValidator(BaseModel):
    mealtime: str
    days: str

    # ✅ 허용된 값 목록
    ALLOWED_MEAL_TIMES: ClassVar[List[str]] = ["아침", "아점", "점심", "점저", "저녁", "간식"]

    # ✅ mealtime 검증
    @field_validator("mealtime")
    def validate_mealtime(cls, value):
        if value not in cls.ALLOWED_MEAL_TIMES:
            raise ValueError(f"mealtime은 {cls.ALLOWED_MEAL_TIMES} 중 하나여야 합니다.")
        return value

    # ✅ days 검증 (1~28의 숫자로 된 문자열만 허용)
    @field_validator("days")
    def validate_days(cls, value):
        day_list = value.split(",")
        for day in day_list:
            if not day.isdigit():
                raise ValueError("days는 숫자만 포함해야 하며, 쉼표로 구분해야 합니다.")
            num = int(day)
            if num < 1 or num > 28:
                raise ValueError("days의 각 값은 1부터 31 사이여야 합니다.")
        return value


class RoutineFoodResponse(BaseModel):
    id: str
    routine_id: str
    food_label: int | None = None
    food_name: str
    quantity: int


class RoutineFoodGroupResponse(RoutineFoodResponse):
    is_clear: bool


class TrackRoutineResponse(BaseModel):
    id: str
    track_id: str
    title: str
    calorie: float
    delete: bool
    mealtime: MealTime
    days: int
    clock: time
    routine_foods: Optional[List[RoutineFoodResponse]]


class RoutineGroupResponse(TrackRoutineResponse):
    is_clear: bool
    routine_foods: Optional[List[RoutineFoodGroupResponse]]


class RoutineFoodRequest(BaseModel):
    food_label: Optional[int] = None
    quantity: int
    food_name: Optional[str] = None


class TrackResponse(BaseModel):
    id: str
    name: str
    duration: int
    start_date: date
    finish_date: date
    routines: List[TrackRoutineResponse]

    class Config:
        from_attributes = True  # ORM 객체를 자동 변환 지원


class CreateTrackBody(BaseModel):
    name: str
    duration: int
    # start_date: date

    ALLOWED_DURATION: ClassVar[List[int]] = [3, 7, 14, 21, 28]

    @field_validator("duration")
    def validate_duration(cls, value):
        if value not in cls.ALLOWED_DURATION:
            raise ValueError(f"duration은 {cls.ALLOWED_DURATION} 중 하나여야 합니다.")
        return value

    # @field_validator("start_date")
    # def validate_start_date(cls, value):
    #     if value < date.today():
    #         raise ValueError("start_date must be today or later")
    #     return value


class CreateTrackRoutineBody(DateValidator):
    track_id: str
    title: str
    calorie: float
    days: str
    mealtime: str

    foods: List[RoutineFoodRequest]


class UpdateTrackBody(BaseModel):
    name: str


class UpdateRoutineBody(DateValidator):
    title: str
    calorie: float
    days: str
    mealtime: str


class TrackUpdateResponse(CreateTrackBody):
    id: str
    name: str
    duration: int
    start_date: datetime
    finish_date: datetime


class TrackParticipantResponse(BaseModel):
    id: str
    user_id: str
    track_id: str
    joined_at: datetime


class TrackStartBody(BaseModel):
    start_date: date

    @field_validator('start_date')
    def validate_start_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("start_date는 오늘보다 과거일 수 없습니다.")
        return v


class TrackRoutineList(BaseModel):
    routine_date_id: str
    title: str
    calorie: int
    date: int
    mealtime: MealTime


class RoutineCheckResponse(BaseModel):
    id: str
    routine_id: str
    user_id: str
    is_complete: bool
    check_time: datetime
