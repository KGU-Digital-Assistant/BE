from datetime import datetime
from typing import Optional, ClassVar, List

from pydantic import BaseModel, field_validator
from enum import Enum


class MealTime(Enum):
    BREAKFAST = 'BREAKFAST'
    BRUNCH = 'BRUNCH'  #아점
    LUNCH = 'LUNCH'
    LINNER = 'LINNER'  #점저
    DINNER = 'DINNER'
    SNACK = 'SNACK' # 간식


class FlagStatus(Enum):
    READY = "READY"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"


class TrackRoutineDateResponse(BaseModel):
    id: str
    routine_id: str
    weekday: int
    meal_time: MealTime
    date: int #몇일차인지


class TrackRoutineResponse(BaseModel):
    id: str
    track_id: str
    title: str
    calorie: float
    delete: bool
    routine_dates: List[TrackRoutineDateResponse]


class TrackResponse(BaseModel):
    id: str
    name: str
    duration: int
    start_date: datetime
    finish_date: datetime
    routines: List[TrackRoutineResponse]

    class Config:
        from_attributes = True  # ORM 객체를 자동 변환 지원


class CreateTrackBody(BaseModel):
    name: str
    duration: int

    ALLOWED_DURATION: ClassVar[List[int]] = [3, 5, 7, 14, 30, 60]

    @field_validator("duration")
    def validate_duration(cls, value):
        if value not in cls.ALLOWED_DURATION:
            raise ValueError(f"duration은 {cls.ALLOWED_DURATION} 중 하나여야 합니다.")
        return value


class DateValidator(BaseModel):
    meal_time: str
    weekday: str

    # ✅ 허용된 값 목록
    ALLOWED_MEAL_TIMES: ClassVar[List[str]] = ["아침", "아점", "점심", "점저", "저녁", "간식"]
    ALLOWED_WEEKDAYS: ClassVar[List[str]] = ["월", "화", "수", "목", "금", "토", "일"]

    # ✅ meal_time 검증
    @field_validator("meal_time")
    def validate_meal_time(cls, value):
        if value not in cls.ALLOWED_MEAL_TIMES:
            raise ValueError(f"meal_time은 {cls.ALLOWED_MEAL_TIMES} 중 하나여야 합니다.")
        return value

    # ✅ weekday 검증
    @field_validator("weekday")
    def validate_weekday(cls, value):
        for v in value:
            if v not in cls.ALLOWED_WEEKDAYS:
                raise ValueError(f"weekday는 {cls.ALLOWED_WEEKDAYS} 중 하나여야 합니다.")
        return value


class CreateTrackRoutineBody(DateValidator):
    track_id: str
    title: str
    meal_time: str
    weekday: str


class UpdateTrackBody(CreateTrackBody):
    name: str
    duration: int


class UpdateRoutineBody(BaseModel):
    title: str
    calorie: float


class UpdateRoutineDateBody(DateValidator):
    meal_time: str
    weekday: str


class TrackUpdateResponse(CreateTrackBody):
    id: str
    name: str
    duration: int
    start_date: datetime
    finish_date: datetime
