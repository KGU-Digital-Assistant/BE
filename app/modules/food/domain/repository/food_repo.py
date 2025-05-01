from abc import ABCMeta, abstractmethod


class IFoodRepository(metaclass=ABCMeta):

    @abstractmethod
    def find_food_by_name(self, name: str):
        raise NotImplementedError

    @abstractmethod
    def find_food_by_label(self, label: int):
        raise NotImplementedError

