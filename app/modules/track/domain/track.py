from dataclasses import dataclass, field
from typing import List, Optional
import datetime
from dataclasses import dataclass

from app.modules.track.interface.schema.track_schema import MealTime


@dataclass
class TrackRoutine:  # 식단트랙 루틴
    id: str
    track_id: str
    title: str
    mealtime: MealTime
    days: int  # 몇일 차 인지
    calorie: float = field(default=0.0)  # 목표 칼로리
    delete: bool = field(default=False)  # 삭제 여부
    clock: datetime.time = field(default_factory=lambda: datetime.time(0, 0, 0))
    image_url: str = None

    track: Optional["Track"] = field(default=None)  # ✅ 기본값 추가
    routine_foods: Optional[List["RoutineFood"]] = field(default=None)


@dataclass
class RoutineCheck:
    id: str
    routine_id: str
    user_id: str
    is_complete: bool
    check_time: datetime = field(default_factory=lambda: datetime.datetime.now())

    # routine: Optional["Routine"] = field(default=None)
    # user: Optional["User"] = field(default=None)


@dataclass
class Track:  # 식단트랙
    id: str
    user_id: str
    name: str = field(default="새로운 식단 트랙")
    icon: Optional[str] = None
    origin_track_id: Optional[str] = None
    #water: float = field(default=0.0)
    #coffee: float = field(default=0.0)
    #alcohol: float = field(default=0.0)
    duration: int = field(default=0)
    delete: bool = field(default=False)
    cheating_count: int = field(default=0)
    create_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    start_date: datetime.date = None
    finish_date: datetime.date = None
    share_count: int = field(default=0)
    alone: bool = field(default=True)
    daily_calorie: float = field(default=0.0)
    image_url: Optional[str] = None

    # 관계 매핑을 위한 필드
    routines: List[TrackRoutine] = field(default_factory=list)

