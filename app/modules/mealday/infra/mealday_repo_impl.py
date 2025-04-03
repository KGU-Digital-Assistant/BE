from abc import ABC
from ulid import ULID
from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta
from calendar import monthrange
from database import SessionLocal, get_db
from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay as MealDayVO
from modules.mealday.domain.mealday import Meal as MealVO
from modules.mealday.infra.db_models.mealday import MealDay, Dish, Meal
from modules.food.infra.db_models.food import Food
from modules.mealday.interface.schema.mealday_schema import Dish_with_datetime,Dish_Full
from modules.track.interface.schema.track_schema import MealTime
from modules.track.infra.db_models.track_participant import TrackParticipant
from modules.track.infra.db_models.track import Track
from utils.db_utils import row_to_dict
from core.fcm import bucket
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error


class MealDayRepository(IMealDayRepository, ABC):

    def save_mealday(self, mealday: MealDayVO):
        with SessionLocal() as db:
            new_mealday = MealDay(
                id=mealday.id,
                user_id=mealday.user_id,
                record_date=mealday.record_date,
                update_datetime=datetime.utcnow(),
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
                        update_datetime=datetime.utcnow(),
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

    def save_many_mealday_by_track_id(self, user_id: str, track_id: str):
        with SessionLocal() as db:
            track = db.query(Track).filter(Track.id == track_id).first()
            date_iter = track.start_date
            last_day =track.finish_date
            count = 0
            while date_iter <= last_day:
                meal = db.query(MealDay).filter(MealDay.user_id == user_id, MealDay.record_date == date_iter).first()
                if not meal:
                    new_mealday = MealDay(
                        id=str(ULID()),
                        user_id=user_id,
                        record_date=date_iter,
                        update_datetime=datetime.utcnow(),
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
                        track_id=track_id
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
            mealday.update_datetime = datetime.utcnow()
            db.commit()
            return mealday

    ########################################################################
    ##############MealHour##################################################
    ########################################################################

    def find_meal_by_date(self, user_id: str, record_date: date, mealtime: MealTime):
        with SessionLocal() as db:
            return (
                db.query(Meal)
                .select_from(MealDay)
                .join(Meal, MealDay.id == Meal.mealday_id)
                .join(Dish, Dish.meal_id == Meal.id)
                .filter(MealDay.user_id == user_id, MealDay.record_date == record_date, Meal.mealtime == mealtime)
                .first()
            )

    def get_all_dishes_by_track_id(self, user_id: str, track_id: str):
        with SessionLocal() as db:
            track = db.query(Track).filter(Track.id == track_id).first()
            date_iter = track.start_date
            last_day =track.finish_date
            dishes=[]
            while date_iter <= last_day:
                mealday = (
                    db.query(MealDay)
                    .options(
                        joinedload(MealDay.meals).joinedload(Meal.dishes)
                    )
                    .filter(
                        MealDay.user_id == user_id,
                        MealDay.record_date == date_iter,
                        MealDay.track_id == track_id
                    )
                    .first()
                )
                if mealday:
                    for meal in mealday.meals:
                        if meal and meal.dishes:
                            dishes_full = []
                            for dish in meal.dishes:
                                picture_url = None
                                if dish.picture and dish.picture != "default":
                                    try:
                                        # 서명된 URL 생성 (URL은 1시간 동안 유효)
                                        blob = bucket.blob(dish.picture)
                                        picture_url = blob.generate_signed_url(expiration=timedelta(hours=1))
                                    except Exception:
                                        raise raise_error(ErrorCode.DISH_NOT_FOUND)
                                dish_data = Dish_Full.from_orm(dish)
                                dish_data.picture = picture_url
                                dishes_full.append(dish_data)

                            dishes.append(Dish_with_datetime(
                                record_date=mealday.record_date,
                                mealtime=meal.mealtime,
                                dish_list=dishes_full
                            ))
                date_iter += timedelta(days=1)

            return dishes


    def create_meal(self, user_id: str, record_date: date, mealtime: MealTime):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.user_id==user_id, MealDay.record_date==record_date).first()
            new_meal = Meal(
                check = False,
                mealtime = mealtime,
                mealday_id = mealday.id
            )
            db.add(new_meal)
            db.commit()
            return MealVO(**row_to_dict(new_meal))

    def create_dishes(self, user_id: str, meal_id: str,name: List[str], calorie: List[str], picture_path: List[str], mealday_id: str):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id ==mealday_id).first()
            trackparticipant = db.query(TrackParticipant).filter(TrackParticipant.user_id==user_id,TrackParticipant.track_id==mealday.track_id).first()
            for i in range(len(name)):
                food = db.query(Food).filter(Food.name == name[i]).first()
                dish_label = food.label if food and food.label is not None else None
                new_dish = Dish(
                    id=str(ULID()),
                    user_id=user_id,
                    meal_id=meal_id,
                    name=name[i],
                    picture=picture_path[i],
                    text=None,
                    record_datetime=datetime.utcnow(),
                    update_datetime=datetime.utcnow(),
                    heart = False,
                    carb = 0.0,
                    protein =0.0,
                    fat = 0.0,
                    calorie = calorie[i],
                    unit = "gram",
                    size = 100.0,
                    track_goal = False,
                    label = dish_label,
                    trackpart_id = trackparticipant.id,
                )
                db.add(new_dish)
                mealday.nowcalorie += calorie[i]
            db.add(mealday)
            db.commit()

    def find_dish(self, user_id: str, dish_id: str):
        with SessionLocal() as db:
            return db.query(Dish).filter(Dish.user_id==user_id, Dish.id == dish_id).first()

    def delete_dish(self, user_id: str, dish_id: str):
        with SessionLocal() as db:
            mealday = (
                db.query(MealDay)
                .join(Meal, MealDay.id == Meal.mealday_id)
                .join(Dish, Dish.meal_id == Meal.id)
                .filter(Dish.id == dish_id)
                .first()
            )
            if mealday is None:
                return None
            dish = db.query(Dish).filter(Dish.id == dish_id, Dish.user_id==user_id).first()
            if dish is None:
                return None
            mealday.carb -= dish.carb
            mealday.protein -= dish.protein
            mealday.fat -= dish.fat
            mealday.nowcalorie -= dish.calorie
            mealday.update_datetime = datetime.utcnow()
            picture_path=dish.picture
            db.delete(dish)
            db.commit()
            return picture_path

    def update_dish(self, _dish: Dish, percent: float):
        with SessionLocal() as db:
            dish = db.query(Dish).filter(Dish.id == _dish.id).first()
            if percent > 0:
                mealday = (
                    db.query(MealDay)
                    .join(Meal, MealDay.id == Meal.mealday_id)
                    .join(Dish, Dish.meal_id == Meal.id)
                    .filter(Dish.id == dish.id)
                    .first()
                )
                mealday.carb -= (-_dish.carb + dish.carb)
                mealday.protein -= (-_dish.protein + dish.protein)
                mealday.fat -= (-_dish.fat + dish.fat)
                mealday.nowcalorie -= (-_dish.calorie + dish.calorie)
                mealday.update_datetime = datetime.utcnow()
            dish.heart = _dish.heart
            dish.track_goal = _dish.track_goal
            dish.update_dateime = datetime.utcnow()
            dish.size = _dish.size
            dish.carb = _dish.carb
            dish.protein = _dish.protein
            dish.fat = _dish.fat
            dish.calorie = _dish.calorie
            db.commit()
            return dish
