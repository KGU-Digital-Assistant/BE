from abc import ABC
from app.database import SessionLocal
from app.modules.food.domain.repository.food_repo import IFoodRepository
from app.modules.food.domain.food import Food as FoodVO
from app.modules.food.infra.db_models.food import Food
from app.utils.db_utils import row_to_dict


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
