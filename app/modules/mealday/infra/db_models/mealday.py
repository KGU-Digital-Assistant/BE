from datetime import date, datetime
import ulid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, Float, ForeignKey, UniqueConstraint, DateTime, Enum, Boolean, Index, Table, Column
from database import Base
from modules.track.interface.schema.track_schema import MealTime


class MealDay(Base):
    __tablename__ = "MealDay"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.new()))
    user_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("User.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    update_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow())
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

    meals: Mapped[list["Meal"]] = relationship("Meal", back_populates="mealday", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('user_id', 'record_date', name='_user_date_daily_uc'),
        Index('_user_date_index', 'user_id', 'record_date') ##조회 성능향상
    )

class Meal(Base):
    __tablename__ = "Meal"
    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False,default=lambda: str(ulid.new()))
    mealday_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("MealDay.id"), nullable=False)
    mealtime: Mapped[MealTime] = mapped_column(Enum(MealTime), nullable=False) #LUNCH, DINNER 등
    check: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    mealday: Mapped["MealDay"] = relationship("MealDay", back_populates="meals")
    dishes: Mapped[list["Dish"]] = relationship("Dish", back_populates="meal", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('mealday_id', 'mealtime', name='_mealday_id_mealtime_uc'),
    )


class Dish(Base):
    __tablename__ = "Dish"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.new()))
    user_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("User.id"), nullable=False)
    meal_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("Meal.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False, default="새로운 식단 등록")
    picture: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True) # 사진경로
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
    label: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    trackpart_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("TrackParticipant.id"), nullable=True)
    meal: Mapped["Meal"] = relationship("Meal", back_populates="dishes")

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
