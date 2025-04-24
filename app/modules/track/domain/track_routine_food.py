import datetime
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class RoutineFood:
    id: str
    routine_id: str
    food_label: int
    food_name: str
    quantity: int = field(default=1)

    track_routine: Optional["TrackRoutine"] = field(default=None)
    food: Optional["Food"] = field(default=None)


@dataclass
class RoutineFoodCheck:
    id: str
    routine_food_id: str
    dish_id: str
    user_id: str
    is_complete: bool = field(default=False)
    check_time: datetime = field(default=datetime.utcnow())
