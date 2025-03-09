from abc import ABC
from ulid import ULID
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from calendar import monthrange
from database import SessionLocal, get_db
from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay as MealDayVO
from modules.mealday.domain.mealday import MealHour as MealHourVO
from modules.mealday.infra.db_models.mealday import MealDay, MealHour, Food
from modules.mealday.interface.schema.mealday_schema import MealDayResponse_RecordCount
from modules.track.interface.schema.track_schema import MealTime
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error


class MealDayRepository(IMealDayRepository, ABC):

    def save_mealday(self, mealday: MealDayVO):
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
            return MealDayVO(**row_to_dict(new_mealday))

    def save_many_mealday(self, user_id: str, first_day: date, last_day: date):
        with SessionLocal() as db:
            date_iter = first_day
            count = 0
            while date_iter <= last_day:
                meal = db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == date_iter).first()
                if not meal:
                    new_mealday = MealDay(
                        id=str(ULID()),
                        user_id=user_id,
                        record_date=date_iter,
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
                    db.add(new_mealday)
                    count += 1
                date_iter += timedelta(days=1)
            if count>=1:
                db.commit()
            return count

    def find_by_date(self, user_id: str, record_date: date) -> MealDayVO:
        with SessionLocal() as db:
            return db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == record_date).first()

    def find_record_count(self, user_id: str, first_day: str, last_day: str):
        with SessionLocal() as db:
            record_count = 0
            calorie = 0
            date_iter = first_day
            while date_iter <= last_day:
                meal = db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == date_iter).first()
                date_iter += timedelta(days=1)
                if meal and meal.nowcalorie > 0.0:
                    record_count += 1
                    calorie += meal.nowcalorie

            return MealDayResponse_RecordCount(record_count=record_count, calorie=calorie)

    def find_by_year_month(self, user_id:str, year: int, month: int):
        with SessionLocal() as db:
            return (db.query(MealDay).order_by(MealDay.record_date.asc()).
                     filter(MealDay.user_id == user_id,
                            MealDay.record_date >= date(year, month, 1),
                            MealDay.record_date <= datetime(year, month, monthrange(year, month)[1]).date()).all())

    def update_mealday(self, _mealday: MealDay):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id == _mealday.id, MealDay.record_date == _mealday.record_date).first()
            mealday.weight = _mealday.weight
            mealday.burncalorie = _mealday.burncalorie
            mealday.water = _mealday.water
            mealday.coffee = _mealday.coffee
            mealday.alcohol = _mealday.alcohol
            db.commit()
            return mealday

    ########################################################################
    ##############MealHour##################################################
    ########################################################################

    def find_mealhour_by_id(self, user_id: str, mealhour_id: str):
        with SessionLocal() as db:
            return db.query(MealHour).filter(MealHour.id == mealhour_id, MealHour.user_id==user_id).first()


    def find_mealhour_by_date(self, user_id: str, record_date: date, mealtime: MealTime):
        with SessionLocal() as db:
            return (
                db.query(MealHour)
                .join(MealDay, MealHour.daymeal_id == MealDay.id)
                .filter(MealDay.user_id == user_id, MealDay.record_date == record_date, MealHour.meal_time == mealtime)
                .first()
            )

    def find_mealhour_all(self, user_id: str, record_date: date):
        with SessionLocal() as db:
            today_meals = (
                db.query(MealHour)
                .join(MealDay, MealHour.daymeal_id == MealDay.id)
                .filter(MealDay.user_id == user_id, MealDay.record_date == record_date)
                .all()
            )
            meals = []
            for meal in today_meals:
                meals.append(meal)
            return meals

    def create_mealhour(self, user_id: str, record_datetime: datetime, mealtime: MealTime, file_name: str,
                        food_label: int, text: str):
        with SessionLocal() as db:
            food_info = db.query(Food).filter(Food.label == food_label).first()
            mealday = db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == record_datetime.date()).first()
            mealday.carb += food_info.carb
            mealday.protein += food_info.protein
            mealday.fat += food_info.fat
            mealday.nowcalorie += food_info.calorie
            mealhour = MealHour(
                id=str(ULID()),
                user_id=user_id,
                daymeal_id=mealday.id,
                meal_time=mealtime,
                name=food_info.name,
                picture=file_name,
                text=text,
                record_datetime=record_datetime,  # 현재 시간을 기본값으로 설정
                heart=False,
                carb=food_info.carb,
                protein=food_info.protein,
                fat=food_info.fat,
                calorie=food_info.calorie,
                unit="gram",
                size=food_info.size,
                track_goal=None,
                label=food_label
            )
            db.add(mealhour)
            db.commit()
            return

    def delete_mealhour(self, user_id: str, record_date: date, mealtime: MealTime):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date==record_date).first()
            if mealday is None:
                return None
            mealhour = db.query(MealHour).filter(MealHour.daymeal_id == mealday.id, MealHour.meal_time==mealtime).first()
            if mealhour is None:
                return None
            mealday.carb -= mealhour.carb
            mealday.protein -= mealhour.protein
            mealday.fat -= mealhour.fat
            mealday.nowcalorie -= mealhour.calorie
            picture_path=mealhour.picture
            db.delete(mealhour)
            db.commit()
            return picture_path

    def update_mealhour(self, _mealhour: MealHour, percent: float):
        with SessionLocal() as db:
            mealhour = db.query(MealHour).filter(MealHour.id == _mealhour.id).first()
            if percent > 0:
                mealday = db.query(MealDay).filter(MealDay.id == mealhour.daymeal_id).first()
                mealday.carb -= (-_mealhour.carb + mealhour.carb)
                mealday.protein -= (-_mealhour.protein + mealhour.protein)
                mealday.fat -= (-_mealhour.fat + mealhour.fat)
                mealday.nowcalorie -= (-_mealhour.calorie + mealhour.calorie)
            mealhour.heart = _mealhour.heart
            mealhour.track_goal = _mealhour.track_goal
            mealhour.size = _mealhour.size
            mealhour.carb = _mealhour.carb
            mealhour.protein = _mealhour.protein
            mealhour.fat = _mealhour.fat
            mealhour.calorie = _mealhour.calorie
            db.commit()
            return mealhour

    def find_food(self, label: int):
        with SessionLocal() as db:
            return db.query(Food).filter(Food.label == label).first()
