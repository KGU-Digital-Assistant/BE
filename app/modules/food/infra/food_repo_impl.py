from abc import ABC

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.modules.food.domain.repository.food_repo import IFoodRepository
from app.modules.food.domain.food import Food as FoodVO
from app.modules.food.infra.db_models.food import Food
from app.utils.db_utils import row_to_dict
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error


class FoodRepository(IFoodRepository, ABC):

    def find_food_by_name(self, name: str):
        with SessionLocal() as db:
            return db.query(Food).filter(Food.name.like(f"%{name}%")).all()

    def find_food_by_label(self, label: int):
        with SessionLocal() as db:
            food = db.query(Food).filter(Food.label == label).first()
            if food is None:
                return None
            return FoodVO(**row_to_dict(food))

    def insert_food_data(self, food_vo_list):
        with SessionLocal() as db:
            food_list = []
            for food_vo in food_vo_list:
                food_list.append(Food(
                    **food_vo.__dict__
                ))
            try:
                db.bulk_save_objects(food_list)
                db.commit()
            except IntegrityError:
                db.rollback()
                raise raise_error(ErrorCode.FOOD_EXISTS)
