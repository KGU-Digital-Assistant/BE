from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Enum, Time

from app.modules.track.interface.schema.track_schema import FlagStatus


class TrackParticipant(Base):
    __tablename__ = "TrackParticipant"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    track_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("Track.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    status: Mapped[FlagStatus] = mapped_column(Enum(FlagStatus, create_type=True), default=FlagStatus.READY, nullable=False)
