from abc import ABCMeta, abstractmethod

from datetime import date, datetime
from typing import List
from modules.user.domain.user import User as User
from modules.mealday.domain.mealday import MealDay as MealDay
from modules.mealday.domain.mealday import Dish as Dish
from modules.track.domain.track import TrackRoutine as TrackRoutine
from modules.food.domain.food import Food as Food
from modules.mealday.interface.schema.mealday_schema import CreateDishBody
from modules.track.interface.schema.track_schema import MealTime

class IMealDayRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_mealday(self, mealday: MealDay):
        raise NotImplementedError

    @abstractmethod
    def save_many_mealday(self, user_id: str, track_id: str, first_day: date, last_day: date):
        raise NotImplementedError

    @abstractmethod
    def find_by_date(self, user_id: str, record_date: date) -> MealDay:
        raise NotImplementedError

    @abstractmethod
    def update_mealday(self, _mealday: MealDay):
        raise NotImplementedError

    ########################################################################
    ##############  Dish##################################################
    ########################################################################

    @abstractmethod
    def create_dish_trackroutine(self, user_id: str, mealday_id: str, trackroutine: TrackRoutine,
                                 trackpart_id: str, picture_path: str, food: Food | None, label: int | None, name: str | None):
        raise NotImplementedError

    @abstractmethod
    def create_dish(self, user_id: str, mealday_id: str, body: CreateDishBody, trackpart_id: str, mealtime: MealTime, food: Food):
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

    # @abstractmethod
    # def get_all_dishes_by_track_id(self, user_id: str, track_id: str):
    #     raise NotImplementedError

    # @abstractmethod
    # def create_dishes(self, user_id: str, meal_id: str,name: List[str], calorie: List[str], picture_path: List[str], mealday_id: str):
    #     raise NotImplementedError