from fastapi import HTTPException, File, Form, UploadFile
import os, json
from typing import List
from ulid import ULID
from urllib.parse import quote
from dependency_injector.wiring import inject
from calendar import monthrange
from datetime import date, datetime, timedelta, time
from core.fcm import bucket

import modules.user.application.user_service
import requests

from core.fcm import send_fcm_data_noti
from modules.user.domain.repository.user_repo import IUserRepository
from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.mealday.domain.mealday import MealDay as MealDayV0
from modules.track.interface.schema.track_schema import MealTime
from modules.mealday.interface.schema.mealday_schema import CreateMealDayBody, MealDayResponse_Full, \
    UpdateMealDayBody, UpdateDishBody
from utils.crypto import Crypto
from utils.db_utils import orm_to_pydantic, dataclass_to_pydantic
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error

class MealDayService:
    @inject
    def __init__(
            self,
            mealday_repo: IMealDayRepository,
            user_repo: IUserRepository,
            crypto: Crypto,
    ):
        self.mealday_repo = mealday_repo
        self.user_repo = user_repo
        self.crypto = crypto

    def invert_daytime_to_date(self, daytime: str)->date:
        try:
            record_date = datetime.strptime(daytime, '%Y-%m-%d').date()
        except ValueError:
            raise ErrorCode.INVALID_FORMAT
        return record_date

    def create_mealday(self, user_id: str, daytime: date)->MealDayV0:
        new_mealday: MealDayV0 = MealDayV0(
            id=str(ULID()),
            user_id=user_id,
            record_date=daytime,
            update_datetime=datetime.utcnow(),
            water=0.0,
            coffee=0.0,
            alcohol=0.0,
            carb=0.0,
            protein=0.0,
            fat=0.0,
            cheating=0,
            goalcalorie=0.0,
            nowcalorie=0.0,
            burncalorie=0.0,
            gb_carb=None,
            gb_protein=None,
            gb_fat=None,
            weight=0.0,
            routine_success_rate=None,
            track_id=None
        )
        return new_mealday

    def create_mealday_by_date(self, user_id: str, daytime: str):
        record_date = self.invert_daytime_to_date(daytime)

        _mealday_date = None

        try:
            _mealday_date = self.mealday_repo.find_by_date(user_id = user_id, record_date = record_date)
        except HTTPException as e:
            if e.status_code != 404:
                raise HTTPException(status_code=e.status_code, detail=e.detail)

        if _mealday_date:
            return _mealday_date

        new_mealday = self.create_mealday(user_id, record_date)

        return dataclass_to_pydantic(self.mealday_repo.save_mealday(new_mealday), MealDayResponse_Full)

    def create_mealday_by_month(self, user_id: str, year: int, month: int):
        try:
            # 주어진 월의 첫날과 마지막 날을 구합니다.
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
        except ValueError:
            raise ErrorCode.INVALID_FORMAT

        count = self.mealday_repo.save_many_mealday(user_id, first_day = first_day, last_day = last_day)
        return count

    def create_mealday_by_track_id(self, user_id: str, track_id: str):
        count = self.mealday_repo.save_many_mealday_by_track_id(user_id = user_id, track_id = track_id)
        return count

    def find_mealday_by_date(self, user_id: str, record_date: date):
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        return mealday

    def find_mealday_by_date(self, user_id: str, record_date: date):
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        return mealday


    def apply_update_mealday(self, mealday, body: UpdateMealDayBody):
        """사용자 정보 업데이트 적용"""
        if body.weight: mealday.weight = body.weight
        if body.burncalorie: mealday.burncalorie = body.burncalorie
        if body.water: mealday.water = body.water
        if body.coffee: mealday.coffee = body.coffee
        if body.alcohol: mealday.alcohol = body.alcohol
    def update_mealday(self, user_id: str, daytime: str, body: UpdateMealDayBody):
        record_date = self.invert_daytime_to_date(daytime)
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        self.apply_update_mealday(mealday,body)
        return self.mealday_repo.update_mealday(mealday)

########################################################################
##############DISH 및 MEAL##################################################
########################################################################

    def create_file_name(self, user_id: str):
        time = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"{user_id}_{time}"
        return filename

    def moose(self, user_id: str, file: File(...)):
        # 고유한 파일 이름 생성
        file_id = self.create_file_name(user_id=user_id)

        # Firebase Storage에 파일 업로드
        temp_blob = bucket.blob(f"temp/{file_id}")
        temp_blob.upload_from_file(file.file, content_type=file.content_type)

        # Yolov 서버로 파일 전송(yolov 서버가 firebase 사진에 접근)
        url = temp_blob.generate_signed_url(expiration=timedelta(hours=1))  # 60분 유효url
        print(url)
        encoded_url = quote(url, safe='')

        # YOLO 서버에 POST 요청을 보내고, 응답 받기
        #response = requests.post(f"https://hamster-delicate-sparrow.ngrok-free.app/yolo/?url={encoded_url}",
        #                         headers={'accept': 'application/json', 'ngrok-skip-browser-warning': 'hello'})
        response = requests.post(f"http://110.8.6.21/yolo/?url={encoded_url}", headers={'accept': 'application/json'})
        print(response.status_code)
        # Yolov 서버 응답 확인 - 실패시 0 출력
        if response.status_code != 201:
            temp_blob.delete()  # firebase에 저장된 임시파일삭제
            raise ErrorCode.YOLO_FAILED
            return
        # Yolov 서버에서 반환된 정보
        food_info = response.json()
        print(food_info)
        is_success = bool(food_info.get("is_success", False))
        if is_success is False:
            return ErrorCode.NO_FOOD
        return {"file_path": temp_blob.name, "food_info": food_info, "image_url": url}  ## 임시파일이름, food정보, url 반환

    def remove_moose(self, file_path: Form):
        temp_blob = bucket.blob(file_path)
        if temp_blob.exists():
            temp_blob.delete()
            return {"detail": "Temporary file removed"}
        return {"detail": "No Temporary file here"}

    def get_all_dishes_by_track_id(self, user_id: str, track_id: str):
        dishes = self.mealday_repo.get_all_dishes_by_track_id(user_id = user_id, track_id = track_id)
        if dishes is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        return dishes

    def register_dish(self, user_id: str, daytime: str, mealtime: MealTime,
                      name: List[str], calorie: List[float], picture: List[UploadFile] = File(...)):
        record_date = self.invert_daytime_to_date(daytime)
        meal = self.mealday_repo.find_meal_by_date(user_id=user_id,record_date=record_date, mealtime=mealtime)
        if meal is None:
            meal = self.mealday_repo.create_meal(user_id=user_id, record_date=record_date, mealtime=mealtime)

        picture_pathes=[]
        for i in range(len(name)):
            # 파일이 있으면 firebase 업로드 처리, 없으면 None
            if picture and i < len(picture) and picture[i] is not None:
                file = picture[i]
                file_id = self.create_file_name(user_id=user_id)
                blob = bucket.blob(f"meal/{file_id}")
                blob.upload_from_file(file.file, content_type=file.content_type)
                picture_path = blob.name
            else:
                picture_path = "default"
            picture_pathes.append(picture_path)

        self.mealday_repo.create_dishes(user_id=user_id, meal_id=meal.id,name=name, calorie=calorie, picture_path=picture_pathes, mealday_id =meal.mealday_id)


    def find_dish(self, user_id: str, dish_id: str):
        dish = self.mealday_repo.find_dish(user_id= user_id, dish_id= dish_id)
        if dish is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        if dish.picture and dish.picture != "default":
            try:
                # 서명된 URL 생성 (URL은 1시간 동안 유효)
                blob = bucket.blob(dish.picture)
                signed_url = blob.generate_signed_url(expiration=timedelta(hours=1))
            except Exception:
                raise raise_error(ErrorCode.DISH_NOT_FOUND)
            dish.picture = signed_url
        return dish

    def remove_dish(self, user_id: str, dish_id: str):
        picture_path = self.mealday_repo.delete_dish(user_id = user_id, dish_id = dish_id)
        if picture_path == "default":
            return
        elif picture_path is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        else:
            blob = bucket.blob(picture_path)
            if blob.exists():
                blob.delete()

    def apply_update_dish(self, dish, body: UpdateDishBody):
        """사용자 정보 업데이트 적용"""
        if body.heart is not None:
            dish.heart = body.heart
        if body.track_goal is not None:
            dish.track_goal = body.track_goal
        if body.size and body.size > 0:
            old_size = dish.size
            new_size = body.size
            percent = new_size / old_size if old_size > 0 else 1
            dish.size = new_size
            dish.carb *= percent
            dish.protein *= percent
            dish.fat *= percent
            dish.calorie *= percent
            return percent
        return 0

    def update_dish(self, user_id: str, dish_id: str, body: UpdateDishBody):
        dish = self.mealday_repo.find_dish(user_id=user_id,dish_id=dish_id)
        if dish is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        percent = self.apply_update_dish(dish, body) ## 1이면 size변경, 0이면 size변경 X
        return self.mealday_repo.update_dish(dish, percent)

    def get_food_data(self, name: str):
        food= self.mealday_repo.find_food_by_name(name=name)
        if food is None:
            raise raise_error(ErrorCode.NO_FOOD)
        return food