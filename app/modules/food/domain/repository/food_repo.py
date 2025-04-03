from abc import ABCMeta, abstractmethod

class IFoodRepository(metaclass=ABCMeta):

    def find_food_by_name(self, name: str):
        raise NotImplementedError

    @abstractmethod
    def find_food(self, label: int):
        raise NotImplementedError
