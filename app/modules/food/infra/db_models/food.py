from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, Float, ForeignKey, UniqueConstraint, DateTime, Enum, Boolean, Index, Table, Column
from database import Base


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
    picture: Mapped[str] = mapped_column(String(length=255), nullable=True, index=True) # 사진경로

    routine_foods: Mapped[list["RoutineFood"]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )
