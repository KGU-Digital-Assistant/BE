from dataclasses import dataclass, field
from datetime import datetime
from app.modules.track.interface.schema.track_schema import FlagStatus

@dataclass
class TrackParticipant:
    id: str
    user_id: str
    track_id: str
    joined_at: datetime = field(default_factory=datetime.utcnow)
    status: FlagStatus = False

