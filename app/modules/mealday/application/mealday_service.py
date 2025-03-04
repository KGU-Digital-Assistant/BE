from fastapi import HTTPException
from ulid import ULID
from dependency_injector.wiring import inject
from calendar import monthrange
from datetime import date, datetime, timedelta

from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay as MealDayV0
from modules.mealday.interface.schema.mealday_schema import CreateMealDayBody, MealDayResponse_Date, MealDayResponse_Full, \
    UpdateMealDayBody, MealDayResponse_RecordCount
from utils.crypto import Crypto
from utils.db_utils import orm_to_pydantic, dataclass_to_pydantic
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error

class MealDayService:
    @inject
    def __init__(
            self,
            mealday_repo: IMealDayRepository,
            crypto: Crypto,
    ):
        self.mealday_repo = mealday_repo
        self.crypto = crypto

    def create_mealday(self, user_id: str, daytime: date)->MealDayV0:
        new_mealday: MealDayV0 = MealDayV0(
            id=str(ULID()),
            user_id=user_id,
            record_date=daytime,
            water=0.0,
            coffee=0.0,
            alcohol=0.0,
            carb=0.0,
            protein=0.0,
            fat=0.0,
            cheating=0,
            goalcalorie=0.0,
            nowcalorie=0.0,
            burncalorie=0.0,
            gb_carb=None,
            gb_protein=None,
            gb_fat=None,
            weight=0.0,
            routine_success_rate=None,
            track_id=None
        )
        return new_mealday

    def create_mealday_by_date(self, user_id: str, daytime: str):
        try:
            record_date = datetime.strptime(daytime, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        _mealday_date = None

        try:
            _mealday_date = self.mealday_repo.find_by_date(user_id = user_id, record_date = record_date)
        except HTTPException as e:
            if e.status_code != 404:
                raise HTTPException(status_code=e.status_code, detail=e.detail)

        if _mealday_date:
            return _mealday_date

        new_mealday = self.create_mealday(user_id, record_date)

        return dataclass_to_pydantic(self.mealday_repo.save(new_mealday), MealDayResponse_Full)

    def create_mealday_by_month(self, user_id: str, year: int, month: int):
        try:
            # 주어진 월의 첫날과 마지막 날을 구합니다.
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        count = self.mealday_repo.save_many(user_id, first_day = first_day, last_day = last_day)
        return count

    def find_mealday_by_date(self, user_id: str, record_date: date):
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        return mealday

    def find_mealday_todaycalorie_by_date(self, user_id: str, record_date: date):
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        todaycalorie = mealday.nowcalorie - mealday.burncalorie
        goalcalorie = mealday.goalcalorie
        nowcalorie = mealday.nowcalorie
        burncalorie = mealday.burncalorie
        weight = mealday.weight
        return {"todaycalorie": todaycalorie, "goalcalorie": goalcalorie, "nowcalorie": nowcalorie,
                "burncalorie": burncalorie, "weight": weight}

    def get_mealday_record_count_by_date(self, user_id: str, year: int, month: int):
        try:
            # 주어진 월의 첫날과 마지막 날을 구합니다.
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
        body: MealDayResponse_RecordCount = self.mealday_repo.find_record_count(user_id, first_day=first_day,last_day=last_day)

        days = (last_day - first_day).days + 1

        return {"record_count": body.record_count, "days": days}

    def get_mealday_avg_calorie(self, user_id: str, year: int, month: int):
        try:
            # 주어진 월의 첫날과 마지막 날을 구합니다.
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        body: MealDayResponse_RecordCount = self.mealday_repo.find_record_count(user_id,first_day=first_day,last_day=last_day)
        if body.record_count > 0:
            avg_calorie = body.calorie / body.record_count
        else:
            avg_calorie = 0
        return {"calorie": avg_calorie}

    def get_meal_list(self, user_id: str, year: int, month: int):
        meals = self.mealday_repo.find_by_year_month(user_id = user_id, year = year, month =month)
        return meals

    def apply_updates(self, mealday, body: UpdateMealDayBody):
        """사용자 정보 업데이트 적용"""
        if body.weight: mealday.weight = body.weight
        if body.burncalorie: mealday.burncalorie = body.burncalorie
        if body.water: mealday.water = body.water
        if body.coffee: mealday.coffee = body.coffee
        if body.alcohol: mealday.alcohol = body.alcohol
    def update_mealday(self, user_id: str, daytime: str, body: UpdateMealDayBody):
        try:
            daytime = datetime.strptime(daytime, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=daytime)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        self.apply_updates(mealday,body)
        return self.mealday_repo.update(mealday)



