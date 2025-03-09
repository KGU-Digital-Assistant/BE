from datetime import date
import ulid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, Float, ForeignKey, UniqueConstraint, DateTime, Enum, Boolean, Index
from database import Base
from modules.track.interface.schema.track_schema import MealTime


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
    track_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("Track.id"), nullable=True, default=None)

    mealhours: Mapped[list["MealHour"]] = relationship("MealHour", back_populates="mealday", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('user_id', 'record_date', name='_user_date_daily_uc'),
        Index('_user_date_index', 'user_id', 'record_date') ##조회 성능향상
    )

class MealHour(Base):  ##식단게시글 (시간대별)
    __tablename__ = "MealHour"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.new()))
    user_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("User.id"), nullable=False)
    daymeal_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("MealDay.id"), nullable=False)
    meal_time: Mapped[MealTime] = mapped_column(Enum(MealTime), nullable=False) #LUNCH, DINNER 등
    name: Mapped[str] = mapped_column(String(length=255), nullable=False, default="새로운 식단 등록")
    picture: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True) # 사진경로
    text: Mapped[str] = mapped_column(String(length=255), nullable=True, default="내용입력")
    record_datetime: Mapped[str] = mapped_column(DateTime, nullable=False)  ## 등록시점 분단뒤
    heart: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False) #트레이너 HEART 여부
    carb: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    protein: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    fat: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    calorie: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    unit:Mapped[str] = mapped_column(String(length=255), nullable=True, default="gram")  ##저장단위
    size: Mapped[float] = mapped_column(Float, nullable=True, default=0.0) #저장 사이즈
    track_goal: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False) #Track에 맞게 지켰는지 여부
    label: Mapped[int] = mapped_column(Integer, nullable=True, default=None)

    mealday: Mapped["MealDay"] = relationship("MealDay", back_populates="mealhours")
    __table_args__ = (
        UniqueConstraint('daymeal_id', 'meal_time', name='_mealday_time_uc'),
    )

class Food(Base):
    __tablename__ = "Food"
    label: Mapped[int] = mapped_column(Integer,primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(length=26), nullable=True, default="음식이름")
    size: Mapped[float] = mapped_column(Float, nullable=True, default=0.0) #저장 사이즈
    calorie: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    carb: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    sugar: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    fat: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    protein: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    calcium: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    phosphorus: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    sodium: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    potassium: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    magnesium: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    iron: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    zinc: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    cholesterol: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    trans_fat: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)

