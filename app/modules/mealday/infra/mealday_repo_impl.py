from abc import ABC
from ulid import ULID
from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta
from calendar import monthrange
from app.database import SessionLocal, get_db
from app.modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from app.modules.mealday.domain.mealday import MealDay as MealDayVO
from app.modules.mealday.domain.mealday import Dish as DishVO
from app.modules.mealday.infra.db_models.mealday import MealDay, Dish
from app.modules.food.infra.db_models.food import Food
from app.modules.mealday.interface.schema.mealday_schema import DishWithDatetime,DishFull, CreateDishBody
from app.modules.track.interface.schema.track_schema import MealTime
from app.modules.track.infra.db_models.track_participant import TrackParticipant
from app.modules.track.infra.db_models.track import Track, TrackRoutine
from app.utils.db_utils import row_to_dict
from app.core.fcm import bucket
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error


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

    def save_many_mealday(self, user_id: str, track_id: str, first_day: date, last_day: date):
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
    ############## Dish ##################################################
    ########################################################################

    def create_dish_trackroutine(self, user_id: str, mealday_id: str, trackroutine: TrackRoutine,
                                 trackpart_id: str, picture_path: str, food: Food | None, label: int | None, name: str | None):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id == mealday_id).first()
            new_dish = Dish(
                id=str(ULID()),
                user_id=user_id,
                mealday_id=mealday.id,
                mealtime=trackroutine.mealtime,
                days=trackroutine.days,
                name=food.name if food else name,
                picture=picture_path,
                text=None,
                record_datetime=datetime.utcnow(),
                update_datetime=datetime.utcnow(),
                heart=False,
                carb=food.carb if food else 0.0,
                protein=food.protein if food else 0.0,
                fat=food.fat if food else 0.0,
                calorie=food.calorie if food else 700.0,
                unit="gram",
                size=food.size if food else 100.0,
                track_goal=False,
                label=label if label else None,
                trackpart_id=trackpart_id,
            )
            db.add(new_dish)
            mealday.nowcalorie += new_dish.calorie
            mealday.carb += new_dish.carb or 0.0
            mealday.protein += new_dish.protein or 0.0
            mealday.fat += new_dish.fat or 0.0
            db.add(mealday)
            db.commit()
            return DishVO(**row_to_dict(new_dish))

    def create_dish(self, user_id: str, mealday_id: str ,body: CreateDishBody, trackpart_id: str, mealtime: MealTime, food: Food):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id == mealday_id).first()
            new_dish = Dish(
                id=str(ULID()),
                user_id=user_id,
                mealday_id=mealday.id,
                mealtime=mealtime,
                days=body.days,
                name=body.name,
                picture=body.picture,
                text=None,
                record_datetime=datetime.utcnow(),
                update_datetime=datetime.utcnow(),
                heart=False,
                carb=food.carb if food else 0.0,
                protein=food.protein if food else 0.0,
                fat=food.fat if food else 0.0,
                calorie=food.calorie if food else 700.0,
                unit="gram",
                size=food.size if food else 100.0,
                track_goal=False,
                label=food.label if food else None,
                trackpart_id=trackpart_id,
            )
            db.add(new_dish)
            mealday.nowcalorie += new_dish.calorie
            mealday.carb += new_dish.carb
            mealday.protein += new_dish.protein
            mealday.fat += new_dish.fat
            db.add(mealday)
            db.commit()
            return DishVO(**row_to_dict(new_dish))

    def find_dish(self, user_id: str, dish_id: str):
        with SessionLocal() as db:
            return db.query(Dish).filter(Dish.user_id==user_id, Dish.id == dish_id).first()

    def delete_dish(self, user_id: str, dish_id: str):
        with SessionLocal() as db:
            mealday = (
                db.query(MealDay)
                .join(Dish, Dish.mealday_id == MealDay.id)
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
            picture_path=dish.image_url
            db.delete(dish)
            db.commit()
            return picture_path

    def update_dish(self, _dish: Dish, percent: float):
        with SessionLocal() as db:
            dish = db.query(Dish).filter(Dish.id == _dish.id).first()
            if percent > 0:
                mealday = (
                    db.query(MealDay)
                    .join(Dish, Dish.mealday_id == MealDay.id)
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


    # def get_all_dishes_by_track_id(self, user_id: str, track_id: str):
    #     with SessionLocal() as db:
    #         track = db.query(Track).filter(Track.id == track_id).first()
    #         date_iter = track.start_date
    #         last_day =track.finish_date
    #         dishes=[]
    #         while date_iter <= last_day:
    #             mealday = (
    #                 db.query(MealDay)
    #                 .options(
    #                     joinedload(MealDay.meals).joinedload(Meal.dishes)
    #                 )
    #                 .filter(
    #                     MealDay.user_id == user_id,
    #                     MealDay.record_date == date_iter,
    #                     MealDay.track_id == track_id
    #                 )
    #                 .first()
    #             )
    #             if mealday:
    #                 for meal in mealday.meals:
    #                     if meal and meal.dishes:
    #                         dishes_full = []
    #                         for dish in meal.dishes:
    #                             picture_url = None
    #                             if dish.picture and dish.picture != "default":
    #                                 try:
    #                                     # 서명된 URL 생성 (URL은 1시간 동안 유효)
    #                                     blob = bucket.blob(dish.picture)
    #                                     picture_url = blob.generate_signed_url(expiration=timedelta(hours=1))
    #                                 except Exception:
    #                                     raise raise_error(ErrorCode.DISH_NOT_FOUND)
    #                             dish_data = Dish_Full.from_orm(dish)
    #                             dish_data.picture = picture_url
    #                             dishes_full.append(dish_data)
    #
    #                         dishes.append(Dish_with_datetime(
    #                             record_date=mealday.record_date,
    #                             mealtime=meal.mealtime,
    #                             dish_list=dishes_full
    #                         ))
    #             date_iter += timedelta(days=1)
    #
    #         return dishes

    # def create_dishes(self, user_id: str, meal_id: str,name: List[str], calorie: List[str], picture_path: List[str], mealday_id: str):
    #     with SessionLocal() as db:
    #         mealday = db.query(MealDay).filter(MealDay.id ==mealday_id).first()
    #         trackparticipant = db.query(TrackParticipant).filter(TrackParticipant.user_id==user_id,TrackParticipant.track_id==mealday.track_id).first()
    #         for i in range(len(name)):
    #             food = db.query(Food).filter(Food.name == name[i]).first()
    #             dish_label = food.label if food and food.label is not None else None
    #             new_dish = Dish(
    #                 id=str(ULID()),
    #                 user_id=user_id,
    #                 meal_id=meal_id,
    #                 name=name[i],
    #                 picture=picture_path[i],
    #                 text=None,
    #                 record_datetime=datetime.utcnow(),
    #                 update_datetime=datetime.utcnow(),
    #                 heart = False,
    #                 carb = 0.0,
    #                 protein =0.0,
    #                 fat = 0.0,
    #                 calorie = calorie[i],
    #                 unit = "gram",
    #                 size = 100.0,
    #                 track_goal = False,
    #                 label = dish_label,
    #                 trackpart_id = trackparticipant.id,
    #             )
    #             db.add(new_dish)
    #             mealday.nowcalorie += calorie[i]
    #         db.add(mealday)
    #         db.commit()


