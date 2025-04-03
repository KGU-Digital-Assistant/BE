from abc import ABCMeta, abstractmethod

from datetime import date, datetime
from typing import List
from modules.user.domain.user import User as User
from modules.mealday.domain.mealday import MealDay as MealDay
from modules.mealday.domain.mealday import Dish as Dish
from modules.track.interface.schema.track_schema import MealTime

class IMealDayRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_mealday(self, mealday: MealDay):
        raise NotImplementedError

    @abstractmethod
    def save_many_mealday(self, user_id: str, first_day: date, last_day: date):
        raise NotImplementedError

    @abstractmethod
    def save_many_mealday_by_track_id(self, user_id: str, track_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_by_date(self, user_id: str, record_date: date) -> MealDay:
        raise NotImplementedError

    @abstractmethod
    def find_by_year_month(self, user_id:str, year: int, month: int):
        raise  NotImplementedError

    @abstractmethod
    def update_mealday(self, _mealday: MealDay):
        raise NotImplementedError

    ########################################################################
    ##############MealHour##################################################
    ########################################################################

    @abstractmethod
    def find_meal_by_date(self, user_id: str, record_date: date):
        raise NotImplementedError
    @abstractmethod
    def get_all_dishes_by_track_id(self, user_id: str, track_id: str):
        raise NotImplementedError

    @abstractmethod
    def create_meal(self, user_id: str, record_date: date, mealtime: MealTime):
        raise NotImplementedError
    @abstractmethod
    def create_dishes(self, user_id: str, meal_id: str,name: List[str], calorie: List[str], picture_path: List[str], mealday_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_dish(self, user_id: str, dish_id: str):
        raise NotImplementedError

    @abstractmethod
    def delete_dish(self, user_id: str, dish_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_dish(self, _dish: Dish, percent: float):
        raise NotImplementedError

