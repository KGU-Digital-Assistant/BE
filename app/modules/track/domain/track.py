from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import ulid
from enum import Enum

from modules.track.infra.db_models.track import TrackRoutine
from modules.track.interface.schema.track_schema import MealTime


@dataclass
class TrackRoutineDate:
    id: str
    routine_id: str
    weekday: int  # 0 ~ 6
    meal_time: MealTime
    date: int  # 몇일 차 인지
    clock: datetime.time = field(default_factory=lambda: datetime.time(0, 0, 0))


@dataclass
class TrackRoutine:  # 식단트랙 루틴
    id: str
    track_id: str
    title: str
    calorie: float = field(default=0.0)  # 목표 칼로리
    delete: bool = field(default=False)  # 삭제 여부
    routine_dates: List[TrackRoutineDate] = field(default_factory=list)
    track: Optional["Track"] = field(default=None)  # ✅ 기본값 추가


@dataclass
class Track:  # 식단트랙
    id: str
    user_id: str
    name: str = field(default="새로운 식단 트랙")
    icon: Optional[str] = None
    origin_track_id: Optional[str] = None
    water: float = field(default=0.0)
    coffee: float = field(default=0.0)
    alcohol: float = field(default=0.0)
    duration: int = field(default=0)
    delete: bool = field(default=False)
    cheating_count: int = field(default=0)
    create_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    start_date: datetime.date = None
    finish_date: datetime.date = None
    share_count: int = field(default=0)
    alone: bool = field(default=True)
    daily_calorie: float = field(default=0.0)

    # 관계 매핑을 위한 필드
    routines: List[TrackRoutine] = field(default_factory=list)
