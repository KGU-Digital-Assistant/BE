import datetime

import sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Enum, Time

from database import Base
import ulid

from modules.track.interface.schema.track_schema import MealTime


class Track(Base):  # 식단트랙
    __tablename__ = "Track"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False)
    icon: Mapped[str] = mapped_column(String, nullable=True)
    origin_track_id: Mapped[str | None] = mapped_column(String(length=26), ForeignKey("Track.id"), nullable=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("User.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(length=255), default="새로운 식단 트랙")
    water: Mapped[float] = mapped_column(Float, default=0)
    coffee: Mapped[float] = mapped_column(Float, default=0)
    alcohol: Mapped[float] = mapped_column(Float, default=0)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # 기간 표현
    delete: Mapped[bool] = mapped_column(Boolean, default=False)  # 트랙 생성자가 삭제 시 다른 사람도 사용 불가
    cheating_count: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=True, default=datetime.date.today)
    finish_date: Mapped[datetime.date] = mapped_column(Date, nullable=True, default=datetime.date.today)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    alone: Mapped[bool] = mapped_column(Boolean, default=True)  # 개인트랙 여부
    daily_calorie: Mapped[float] = mapped_column(Float, default=0)

    routines: Mapped[list["TrackRoutine"]] = relationship("TrackRoutine", back_populates="track", cascade="all, delete-orphan")


class TrackRoutine(Base):  # 식단트랙 루틴
    __tablename__ = "TrackRoutine"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(ulid.new()))
    track_id: Mapped[str] = mapped_column(String(length=26), ForeignKey("Track.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False, default="새로운 루틴")
    calorie: Mapped[float] = mapped_column(Float, nullable=False, default=0)  # 목표 칼로리
    delete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 삭제 여부

    track: Mapped["Track"] = relationship("Track", back_populates="routines")
    routine_dates: Mapped[list["TrackRoutineDate"]] = relationship("TrackRoutineDate", back_populates="routine", cascade="all, delete-orphan")


class TrackRoutineDate(Base):
    __tablename__ = "TrackRoutineDate"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    routine_id: Mapped[str] = mapped_column(String, ForeignKey("TrackRoutine.id"), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 ~ 6
    meal_time: Mapped[MealTime] = mapped_column(Enum(MealTime))
    date: Mapped[int] = mapped_column(Integer, nullable=False) # 몇일 차 인지
    clock: Mapped[datetime.time] = mapped_column(Time, nullable=False, default=lambda: datetime.time(0, 0, 0))

    routine: Mapped["TrackRoutine"] = relationship("TrackRoutine", back_populates="routine_dates")