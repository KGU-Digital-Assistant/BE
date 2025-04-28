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
from modules.mealday.domain.mealday import Dish as DishVO
from modules.mealday.infra.db_models.mealday import MealDay, Dish
from modules.food.infra.db_models.food import Food
from modules.mealday.interface.schema.mealday_schema import Dish_with_datetime,Dish_Full, CreateDishBody
from modules.track.interface.schema.track_schema import MealTime
from modules.track.infra.db_models.track_participant import TrackParticipant
from modules.track.infra.db_models.track import Track, TrackRoutine
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

    def find_by_id(self, mealday_id: str) -> MealDayVO:
        with SessionLocal() as db:
            return db.query(MealDay).filter(MealDay.id == mealday_id).first()

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
                                 trackpart_id: str, image_url: str, quantity: int | None, food: Food | None, label: int | None, name: str | None):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id == mealday_id).first()
            new_dish = Dish(
                id=str(ULID()),
                user_id=user_id,
                mealday_id=mealday.id,
                mealtime=trackroutine.mealtime,
                days=trackroutine.days,
                name=food.name if food else name,
                quantity = quantity,
                image_url=image_url,
                text=None,
                record_datetime=datetime.utcnow(),
                update_datetime=datetime.utcnow(),
                heart=False,
                carb=food.carb * quantity if food else 0.0,
                protein=food.protein * quantity if food else 0.0,
                fat=food.fat * quantity if food else 0.0,
                calorie=food.calorie * quantity if food else 700.0 * quantity,
                unit="gram",
                size=food.size * quantity if food else 100.0,
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

    def create_dish(self, user_id: str, mealday_id: str, body: CreateDishBody,
                    trackpart_id: str, mealtime: MealTime, food: Food, image_path: str):
        with SessionLocal() as db:
            mealday = db.query(MealDay).filter(MealDay.id == mealday_id).first()
            new_dish = Dish(
                id=str(ULID()),
                user_id=user_id,
                mealday_id=mealday.id,
                mealtime=mealtime,
                days=body.days,
                name=food.name if food else body.name,
                quantity=body.quantity,
                image_url=image_path,
                text=None,
                record_datetime=datetime.utcnow(),
                update_datetime=datetime.utcnow(),
                heart=False,
                carb=food.carb * body.quantity if food else 0.0,
                protein=food.protein * body.quantity if food else 0.0,
                fat=food.fat * body.quantity if food else 0.0,
                calorie=food.calorie * body.quantity if food else 700.0 * body.quantity,
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

    def find_dish_all(self, user_id: str, mealday_id: str):
        with SessionLocal() as db:
            return db.query(Dish).filter(Dish.user_id==user_id,Dish.mealday_id==mealday_id).all()

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
            image_url=dish.image_url
            db.delete(dish)
            db.commit()
            return image_url

    def update_dish(self, _dish: Dish, percent: float, image_path: str | None):
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
            dish.image_url = image_path
            dish.track_goal = _dish.track_goal
            dish.label = _dish.label
            dish.quantity =  _dish.quantity
            dish.update_dateime = datetime.utcnow()
            dish.size = _dish.size
            dish.carb = _dish.carb
            dish.protein = _dish.protein
            dish.fat = _dish.fat
            dish.calorie = _dish.calorie
            db.commit()
            return DishVO(**row_to_dict(dish))

    def update_dish_quantity(self, dish_id: str, quantity: int, food: Food | None, name: str | None):
        with SessionLocal() as db:
            dish = db.query(Dish).filter(Dish.id == dish_id).first()
            mealday = (
                db.query(MealDay)
                .join(Dish, Dish.mealday_id == MealDay.id)
                .filter(Dish.id == dish.id)
                .first()
            )
            if dish.label and name: # 라벨 -> 이름으로 변경시
                mealday.carb += (-dish.carb + 0.0)
                mealday.protein += (-dish.protein + 0.0)
                mealday.fat += (-dish.fat + 0.0)
                mealday.nowcalorie += (-dish.calorie + 700 * quantity)
                mealday.update_datetime = datetime.utcnow()
                dish.quantity = quantity
                dish.update_dateime = datetime.utcnow()
                dish.carb = 0
                dish.protein = 0
                dish.fat = 0
                dish.calorie = 700 * quantity
                db.commit()
            elif dish.label is None and food: # 이름 -> 라벨로 변경시
                mealday.carb += (-dish.carb + food.carb)
                mealday.protein += (-dish.protein + food.protein)
                mealday.fat += (-dish.fat + food.fat)
                mealday.nowcalorie += (-dish.calorie + food.calorie * quantity)
                mealday.update_datetime = datetime.utcnow()
                dish.quantity = quantity
                dish.update_dateime = datetime.utcnow()
                dish.carb = 0
                dish.protein = 0
                dish.fat = 0
                dish.calorie = 700 * quantity
                db.commit()
            else: # 이름->이름, 라벨->라벨
                ratio = (float(quantity) / float(dish.quantity))
                mealday.carb += dish.carb * ratio
                mealday.protein += dish.protein * ratio
                mealday.fat += dish.fat * ratio
                mealday.nowcalorie += dish.calorie * ratio
                mealday.update_datetime = datetime.utcnow()
                dish.quantity += quantity
                dish.update_dateime = datetime.utcnow()
                dish.carb = dish.carb + dish.carb * ratio
                dish.protein = dish.protein + dish.protein * ratio
                dish.fat = dish.fat + dish.fat * ratio
                dish.calorie = dish.calorie + dish.calorie * ratio
                db.commit()
            return DishVO(**row_to_dict(dish))

    def update_dish_label_or_name(self, dish_id: str, name: str | None, quantity: int, food: Food | None):
        with SessionLocal() as db:
            dish = db.query(Dish).filter(Dish.id == dish_id).first()
            if dish is None:
                raise raise_error(ErrorCode.DISH_NOT_FOUND)
            mealday = (
                db.query(MealDay)
                .join(Dish, Dish.mealday_id == MealDay.id)
                .filter(Dish.id == dish.id)
                .first()
            )
            mealday.carb -= (-food.carb * quantity + dish.carb) if food else mealday.carb
            mealday.protein -= (-food.protein * quantity + dish.protein) if food else mealday.protein
            mealday.fat -= (-food.fat * quantity + dish.fat) if food else mealday.fat
            mealday.nowcalorie -= (-food.calorie * quantity + dish.calorie) if food else (-700 * quantity + dish.calorie)
            mealday.update_datetime = datetime.utcnow()
            dish.quantity = quantity
            dish.update_dateime = datetime.utcnow()
            dish.carb = food.carb if food else 0.0
            dish.protein = food.protein if food else 0.0
            dish.fat = food.fat if food else 0.0
            dish.size = food.size if food else 100.0
            dish.label = food.label if food else None,
            dish.calorie = food.calorie if food else 700 * quantity
            dish.name = food.name if food else name
            dish.update_datetime = datetime.utcnow()
            db.commit()
            return DishVO(**row_to_dict(dish))

    def update_dish_image(self, dish_id: str, image_path: str):
        with SessionLocal() as db:
            dish = db.query(Dish).filter(Dish.id == dish_id).first()
            if dish is None:
                return None
            dish.image_url = image_path
            db.commit()