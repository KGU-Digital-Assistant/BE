from dependency_injector.wiring import inject
from modules.user.domain.repository.user_repo import IUserRepository
from modules.food.domain.repository.food_repo import IFoodRepository
from utils.crypto import Crypto
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error


class FoodService:
    @inject
    def __init__(
            self,
            food_repo: IFoodRepository,
            user_repo: IUserRepository,
            crypto: Crypto,
    ):
        self.food_repo = food_repo
        self.user_repo = user_repo
        self.crypto = crypto

    def search_food_data(self, name: str):
        if len(name) < 2:
            raise raise_error(ErrorCode.REQUIRE_2LETTER)
        food = self.food_repo.find_food_by_name(name=name)
        if not food:
            raise raise_error(ErrorCode.NO_FOOD)
        return food

    def get_food_data(self, food_label: int):
        return self.food_repo.find_food_by_label(label=food_label)
