import pandas as pd
from dependency_injector.wiring import inject

from app.core.auth import Role, get_admin_user
from app.modules.food.domain.food import Food
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.food.domain.repository.food_repo import IFoodRepository
from app.utils.crypto import Crypto
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error


class FoodService:
    @inject
    def __init__(
            self,
            food_repo: IFoodRepository,
            crypto: Crypto,
    ):
        self.food_repo = food_repo
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

    def insert_food_data(self):
        df = pd.read_excel('food_data.xlsx')

        # 컬럼명 Food 모델에 맞게 리네임
        df.columns = [
            'label', 'name', 'size', 'calorie', 'carb', 'sugar', 'fat', 'protein',
            'calcium', 'phosphorus', 'sodium', 'potassium', 'magnesium', 'iron',
            'zinc', 'cholesterol', 'trans_fat'
        ]

        df['image_url'] = None

        # '-'를 NaN으로 바꾸기
        df.replace('-', pd.NA, inplace=True)

        # NaN을 0으로 채우기
        df.fillna(0, inplace=True)

        food_list = [
            Food(
                label=int(row['label']),
                name=str(row['name']),
                size=float(row['size']),
                calorie=float(row['calorie']),
                carb=float(row['carb']),
                sugar=float(row['sugar']),
                fat=float(row['fat']),
                protein=float(row['protein']),
                calcium=float(row['calcium']),
                phosphorus=float(row['phosphorus']),
                sodium=float(row['sodium']),
                potassium=float(row['potassium']),
                magnesium=float(row['magnesium']),
                iron=float(row['iron']),
                zinc=float(row['zinc']),
                cholesterol=float(row['cholesterol']),
                trans_fat=float(row['trans_fat']),
                image_url=""
            )
            for _, row in df.iterrows()
        ]

        self.food_repo.insert_food_data(food_list)
        return True
