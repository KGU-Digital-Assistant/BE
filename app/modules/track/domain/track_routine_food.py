from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RoutineFood:
    id: str
    routine_id: str
    food_label: int
    food_name: str
    quantity: int = field(default=1)

    track_routine: Optional["TrackRoutine"] = field(default=None)
    food: Optional["Food"] = field(default=None)
