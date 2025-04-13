from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# Routine - Food 중간 테이블
class RoutineFood(Base):
    __tablename__ = "RoutineFood"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False)
    track_routine_id: Mapped[str] = mapped_column(
        ForeignKey("TrackRoutine.id", ondelete="CASCADE"),
    )
    food_label: Mapped[int] = mapped_column(
        ForeignKey("Food.label", ondelete="CASCADE"),
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("track_routine_id", "food_label", name="uq_routine_food_pair"),
    )
    # 관계 설정 (선택 사항)
    track_routine: Mapped["TrackRoutine"] = relationship(
        back_populates="routine_foods",
        passive_deletes=True
    )
    food: Mapped["Food"] = relationship(
        back_populates="routine_foods",
        passive_deletes=True
    )
    # 디쉬 id 추가하기