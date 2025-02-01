from fastapi import HTTPException

from dependency_injector.wiring import inject
from datetime import date

from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay
from modules.mealday.interface.schema.mealday_schema import CreateMealDayBody
from utils.crypto import Crypto
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import CustomException

class MealDayService:
    @inject
    def __init__(
            self,
            mealday_repo: IMealDayRepository,
            crypto: Crypto,
    ):
        self.mealday_repo = mealday_repo
        self.crypto = crypto

    def create_mealday(
            self,
            # background_tasks: BackgroundTasks,
            mealday: CreateMealDayBody,
            id: str
    ):
        _mealday_date = None

        try:
            _mealday_date = self.mealday_repo.find_by_date(user_id = mealday.user_id, record_date = mealday.record_date)
        except HTTPException as e:
            if e.status_code != 404:
                raise HTTPException(status_code=e.status_code, detail=e.detail)

        if _mealday_date:
            return _mealday_date

        new_mealday: MealDay = MealDay(
            user_id=id,
            record_date=mealday.record_date,
        )
        self.mealday_repo.save(new_mealday)

        return new_mealday

    def find_mealday_by_date(self, record_date: date, user_id: str):
        mealday = self.mealday_repo.find_by_date(record_date, user_id)
        if not mealday:
            raise CustomException(ErrorCode.MEALDAY_NOT_FOUND)
        return mealday