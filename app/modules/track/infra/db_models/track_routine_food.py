from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Routine - Food 중간 테이블
class RoutineFood(Base):
    __tablename__ = "RoutineFood"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False)
    routine_id: Mapped[str] = mapped_column(
        ForeignKey("TrackRoutine.id", ondelete="CASCADE"), nullable=False,
    )
    food_label: Mapped[int] = mapped_column(
        ForeignKey("Food.label", ondelete="CASCADE"), nullable=True, ### label없는게 이미지없는text로만 저장한거
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    food_name: Mapped[str] = mapped_column(String, nullable=False)

    # 관계 설정 (선택 사항)
    track_routine: Mapped["TrackRoutine"] = relationship(
        back_populates="routine_foods",
        passive_deletes=True
    )
    food: Mapped["Food"] = relationship(
        back_populates="routine_foods",
        passive_deletes=True
    )

    #유니크 설정
    __table_args__ = (
        UniqueConstraint("routine_id", "food_label", name="uq_routine_food_pair"),    )


class RoutineFoodCheck(Base):
    __tablename__ = "RoutineFoodCheck"
    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False)
    routine_food_id: Mapped[str] = mapped_column(
        ForeignKey("RoutineFood.id", ondelete="CASCADE"), nullable=False,
    )
    dish_id: Mapped[str] = mapped_column(
        ForeignKey("Dish.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE"), nullable=False
    )
    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    check_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("routine_food_id", "dish_id", name="uq_routine_dish_pair"),
    )