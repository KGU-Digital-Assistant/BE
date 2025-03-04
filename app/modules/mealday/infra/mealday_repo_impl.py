from abc import ABC
import ulid
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime
from calendar import monthrange
from database import SessionLocal, get_db
from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay as MealDayV0
from modules.mealday.infra.db_models.mealday import MealDay
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error


class MealDayRepository(IMealDayRepository, ABC):

    def save(self, mealday: MealDayV0):
        with SessionLocal() as db:
            new_mealday = MealDay(
                id=mealday.id,
                user_id=mealday.user_id,
                record_date=mealday.record_date,
                water=mealday.water or 0.0,
                coffee=mealday.coffee or 0.0,
                alcohol=mealday.alcohol or 0.0,
                carb=mealday.carb or 0.0,
                protein=mealday.protein or 0.0,
                fat=mealday.fat or 0.0,
                cheating=mealday.cheating or 0,
                goalcalorie=mealday.goalcalorie or 0.0,
                nowcalorie=mealday.nowcalorie or 0.0,
                burncalorie=mealday.burncalorie or 0.0,
                gb_carb=mealday.gb_carb or None,
                gb_protein=mealday.gb_protein or None,
                gb_fat=mealday.gb_fat or None,
                weight=mealday.weight or 0.0,
                routine_success_rate=mealday.routine_success_rate or None,
                track_id=mealday.track_id or None
            )
            db.add(new_mealday)
            db.commit()
            return MealDayV0(**row_to_dict(new_mealday))
    def find_by_date(self, user_id: str, record_date: date) -> MealDayV0:
        with SessionLocal() as db:
            return db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == record_date).first()

    def find_by_year_month(self, user_id:str, year: int, month: int):
        with SessionLocal() as db:
            return (db.query(MealDay).order_by(MealDay.record_date.asc()).
                     filter(MealDay.user_id == user_id,
                            MealDay.record_date >= date(year, month, 1),
                            MealDay.record_date <= datetime(year, month, monthrange(year, month)[1]).date()).all())

    def update(self, _mealday: MealDay):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id == _mealday.id, MealDay.record_date == _mealday.record_date).first()
            mealday.weight = _mealday.weight
            mealday.burncalorie = _mealday.burncalorie
            mealday.water = _mealday.water
            mealday.coffee = _mealday.coffee
            mealday.alcohol = _mealday.alcohol
            db.commit()
            return mealday
