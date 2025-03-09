from abc import ABCMeta, abstractmethod

from datetime import date, datetime
from modules.user.domain.user import User as User
from modules.mealday.domain.mealday import MealDay as MealDay
from modules.mealday.domain.mealday import MealHour as MealHour
from modules.track.interface.schema.track_schema import MealTime

class IMealDayRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_mealday(self, mealday: MealDay):
        raise NotImplementedError

    @abstractmethod
    def save_many_mealday(self, user_id: str, first_day: date, last_day: date):
        raise NotImplementedError

    @abstractmethod
    def find_by_date(self, user_id: str, record_date: date) -> MealDay:
        raise NotImplementedError

    @abstractmethod
    def find_record_count(self, user_id: str, first_day: date, last_day :date):
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
    def find_mealhour_by_id(self, user_id, str, mealhour_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_mealhour_by_date(self, user_id:str, record_date: date, mealtime: MealTime):
        raise NotImplementedError

    @abstractmethod
    def create_mealhour(self, user_id: str, record_datetime: datetime, mealtime: MealTime, file_name: str,
                        food_label: int, text: str):
        raise NotImplementedError

    @abstractmethod
    def delete_mealhour(self, user_id: str, record_date: date, mealtime: MealTime):
        raise NotImplementedError

    @abstractmethod
    def update_mealhour(self, _mealhour: MealHour, percent: float):
        raise NotImplementedError

    @abstractmethod
    def find_food(self, label: int):
        raise NotImplementedError
