from abc import ABC
from database import SessionLocal
from modules.food.domain.repository.food_repo import IFoodRepository
from modules.food.infra.db_models.food import Food



class FoodRepository(IFoodRepository, ABC):

    def find_food_by_name(self, name: str):
        with SessionLocal() as db:
            return db.query(Food).filter(Food.name == name).first()

    def find_food(self, label: int):
        with SessionLocal() as db:
            return db.query(Food).filter(Food.label == label).first()
