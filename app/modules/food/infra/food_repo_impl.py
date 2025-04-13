from abc import ABC
from database import SessionLocal
from modules.food.domain.repository.food_repo import IFoodRepository
from modules.food.domain.food import Food as FoodVO
from modules.food.infra.db_models.food import Food
from utils.db_utils import row_to_dict


class FoodRepository(IFoodRepository, ABC):

    def find_food_by_name(self, name: str):
        with SessionLocal() as db:
            return db.query(Food).filter(Food.name.like(f"%{name}%")).all()

    def find_food_by_label(self, label: int):
        with SessionLocal() as db:
            food = db.query(Food).filter(Food.label == label).first()
            return FoodVO(**row_to_dict(food))
