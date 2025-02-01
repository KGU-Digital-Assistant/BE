from abc import ABC

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.testing import db
from datetime import date

from database import SessionLocal, get_db
from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay as MealDayV0
from modules.mealday.infra.db_models.mealday import MealDay
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import CustomException

class MealDayRepository(IMealDayRepository, ABC):
    def __init__(self, db: Session):
        self.db = db

    def save(self, mealday: MealDayV0):
        new_mealday = MealDay(
            user_id = MealDayV0.user_id,
            date = MealDayV0.record_date
        )
        self.db.add(new_mealday)
        self.db.commit()

        return new_mealday

    def find_by_date(self, user_id: str, record_date: date) -> MealDayV0:
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == date).first()

        if not mealday:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        return MealDayV0(**row_to_dict(mealday))
