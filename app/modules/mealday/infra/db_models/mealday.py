from datetime import date, datetime
import ulid
import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, Float, ForeignKey, UniqueConstraint, DateTime, Enum, Boolean, Index, Table, Column
from app.database import Base
from app.modules.track.interface.schema.track_schema import MealTime


class MealDay(Base):
    __tablename__ = "MealDay"
    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.ULID()))
    user_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("User.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    update_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=sqlalchemy.text('now()')  # alembic용
    )
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
    track_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("Track.id"), nullable=True, default=None)
    dishes: Mapped[list["Dish"]] = relationship("Dish", back_populates="mealday", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('user_id', 'record_date', name='_user_date_daily_uc'),
        Index('_user_date_index', 'user_id', 'record_date') ##조회 성능향상
    )

class Dish(Base):
    __tablename__ = "Dish"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.ULID()))
    user_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("User.id"), nullable=False)
    mealday_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("MealDay.id"), nullable=False)
    mealtime: Mapped[MealTime] = mapped_column(Enum(MealTime), nullable=False) #LUNCH, DINNER 등
    days: Mapped[int] = mapped_column(Integer, nullable=False, default=0) #일차
    name: Mapped[str] = mapped_column(String(length=255), nullable=False, default="새로운 식단 등록")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1) #수량
    image_url: Mapped[str] = mapped_column(String(length=255), nullable=True, index=True) # 사진경로
    text: Mapped[str] = mapped_column(String(length=255), nullable=True, default="내용입력")
    record_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow())  ## 등록시점 분단뒤
    update_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow())
    heart: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False) #트레이너 HEART 여부
    carb: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    protein: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    fat: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    calorie: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    unit:Mapped[str] = mapped_column(String(length=255), nullable=True, default="gram")  ##저장단위
    size: Mapped[float] = mapped_column(Float, nullable=True, default=0.0) #저장 사이즈
    track_goal: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    label: Mapped[int] = mapped_column(Integer, ForeignKey("Food.label"), nullable=True, default=None)  ## label 필요유무 검토필요
    trackpart_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("TrackParticipant.id"), nullable=True)
    mealday: Mapped["MealDay"] = relationship("MealDay", back_populates="dishes")
