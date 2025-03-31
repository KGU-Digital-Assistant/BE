from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrackParticipant:
    id: str
    user_id: str
    track_id: str
    joined_at: datetime = field(default_factory=datetime.utcnow)
    finished: bool = False

