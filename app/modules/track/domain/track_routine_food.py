from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RoutineFood:
    id: str
    track_routine_id: str
    food_label: int
    quantity: int = field(default=1)

    track_routine: Optional["TrackRoutine"] = field(default=None)
    food: Optional["Food"] = field(default=None)
