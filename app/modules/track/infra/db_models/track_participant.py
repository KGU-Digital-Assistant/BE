from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Enum, Time


class TrackParticipant(Base):
    __tablename__ = "TrackParticipant"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False, unique=True)
    track_id: Mapped[str] = mapped_column(String, ForeignKey("Track.id", ondelete="CASCADE"), nullable=False, unique=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    finished: Mapped[bool] = mapped_column(Boolean, default=False)