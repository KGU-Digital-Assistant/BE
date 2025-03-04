from datetime import date
import ulid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Integer, Float, ForeignKey, UniqueConstraint
from database import Base

class MealDay(Base):
    __tablename__ = "MealDay"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.new()))
    user_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("User.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    water: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    coffee: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    alcohol: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    carb: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    protein: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    fat: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    cheating: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    goalcalorie: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    nowcalorie: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    burncalorie: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    gb_carb: Mapped[str] = mapped_column(String(length=10), nullable=True, default=None)
    gb_protein: Mapped[str] = mapped_column(String(length=10), nullable=True, default=None)
    gb_fat: Mapped[str] = mapped_column(String(length=10), nullable=True, default=None)
    weight: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    routine_success_rate: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    track_id: Mapped[str] = mapped_column(String, ForeignKey("Track.id"), nullable=True, default=None)

    __table_args__ = (
        UniqueConstraint('user_id', 'record_date', name='_user_date_daily_uc'),
    )