from abc import ABCMeta, abstractmethod

from datetime import date, datetime
from typing import List
from app.modules.user.domain.user import User as User
from app.modules.mealday.domain.mealday import MealDay as MealDay
from app.modules.mealday.domain.mealday import Dish as Dish
from app.modules.track.domain.track import TrackRoutine as TrackRoutine
from app.modules.food.domain.food import Food as Food
from app.modules.mealday.interface.schema.mealday_schema import CreateDishBody
from app.modules.track.interface.schema.track_schema import MealTime

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
                                 trackpart_id: str, image_url: str, quantity: int | None, food: Food | None, label: int | None, name: str | None):
        raise NotImplementedError

    @abstractmethod
    def create_dish(self, user_id: str, mealday_id: str, body: CreateDishBody,
                    trackpart_id: str, mealtime: MealTime, food: Food, image_path: str):
        raise NotImplementedError

    @abstractmethod
    def find_dish(self, user_id: str, dish_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_dish_all(self, user_id: str, mealday_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, mealday_id: str) -> MealDay:
        raise NotImplementedError

    @abstractmethod
    def delete_dish(self, user_id: str, dish_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_dish(self, _dish: Dish, percent: float, image_path: str):
        raise NotImplementedError

    @abstractmethod
    def update_dish_quantity(self, dish_id: str, quantity: int, food: Food | None, name: str | None):
        raise NotImplementedError

    @abstractmethod
    def update_dish_label_or_name(self, dish_id: str, name: str | None, quantity: int, food: Food | None):
        raise NotImplementedError

    @abstractmethod
    def update_dish_image(self, dish_id: str, image_path: str):
        raise NotImplementedError