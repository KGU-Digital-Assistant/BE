from abc import ABCMeta, abstractmethod

from datetime import date
from modules.user.domain.user import User as User
from modules.mealday.domain.mealday import MealDay as MealDay

class IMealDayRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, mealday: MealDay):
        raise NotImplementedError

    @abstractmethod
    def save_many(self, user_id: str, first_day: date, last_day: date):
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
    def update(self, _mealday: MealDay):
        raise NotImplementedError

