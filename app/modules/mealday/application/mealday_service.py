from fastapi import HTTPException,File, Form
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
from modules.mealday.interface.schema.mealday_schema import CreateMealDayBody, MealHourResponse_Full_Picture, MealDayResponse_Full, \
    UpdateMealDayBody, MealDayResponse_RecordCount, UpdateMealHourBody
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

    def find_mealday_by_date(self, user_id: str, record_date: date):
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        return mealday

    def find_mealday_todaycalorie_by_date(self, user_id: str, record_date: date):
        mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        todaycalorie = mealday.nowcalorie - mealday.burncalorie
        goalcalorie = mealday.goalcalorie
        nowcalorie = mealday.nowcalorie
        burncalorie = mealday.burncalorie
        weight = mealday.weight
        return {"todaycalorie": todaycalorie, "goalcalorie": goalcalorie, "nowcalorie": nowcalorie,
                "burncalorie": burncalorie, "weight": weight}

    def get_mealday_record_count_by_date(self, user_id: str, year: int, month: int):
        try:
            # 주어진 월의 첫날과 마지막 날을 구합니다.
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
        except ValueError:
            raise ErrorCode.INVALID_FORMAT
        body: MealDayResponse_RecordCount = self.mealday_repo.find_record_count(user_id, first_day=first_day,last_day=last_day)

        days = (last_day - first_day).days + 1

        return {"record_count": body.record_count, "days": days}

    def get_mealday_avg_calorie(self, user_id: str, year: int, month: int):
        try:
            # 주어진 월의 첫날과 마지막 날을 구합니다.
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, monthrange(year, month)[1]).date()
        except ValueError:
            raise ErrorCode.INVALID_FORMAT

        body: MealDayResponse_RecordCount = self.mealday_repo.find_record_count(user_id,first_day=first_day,last_day=last_day)
        if body.record_count > 0:
            avg_calorie = body.calorie / body.record_count
        else:
            avg_calorie = 0
        return {"calorie": avg_calorie}

    def get_meal_list(self, user_id: str, year: int, month: int):
        meals = self.mealday_repo.find_by_year_month(user_id = user_id, year = year, month =month)
        return meals

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
##############MealHour##################################################
########################################################################

    def get_mealhour_by_id(self, user_id: str, mealhour_id: str):
        mealhour = self.mealday_repo.find_mealhour_by_id(user_id=user_id,mealhour_id=mealhour_id)
        if mealhour is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        return mealhour

    def get_mealhour_by_date(self, user_id: str, daytime: str, mealtime: MealTime):
        record_date = self.invert_daytime_to_date(daytime)
        mealhour = self.mealday_repo.find_mealhour_by_date(user_id=user_id, record_date=record_date, mealtime=mealtime)
        if mealhour is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        return mealhour

    def get_mealhour_picture(self, user_id: str, daytime: str, mealtime: MealTime):
        record_date = self.invert_daytime_to_date(daytime)
        mealhour = self.mealday_repo.find_mealhour_by_date(user_id=user_id, record_date=record_date, mealtime=mealtime)
        if mealhour is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        if not mealhour.picture:
            raise ErrorCode.NO_PICTURE

        # 서명된 URL 생성 (URL은 1시간 동안 유효)
        blob = bucket.blob(mealhour.picture)
        signed_url = blob.generate_signed_url(expiration=timedelta(hours=1))

        return {"image_url": signed_url}

    def get_mealhour_by_date_all(self, user_id: str, daytime: str):
        record_date = self.invert_daytime_to_date(daytime)
        mealhours = self.mealday_repo.find_mealhour_all(user_id=user_id, record_date = record_date)
        if mealhours is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        meals_with_url = []
        for meal in mealhours:
            image_url = None
            if meal.picture:
                blob = bucket.blob(meal.picture)
                image_url = blob.generate_signed_url(expiration=timedelta(hours=1))  # 1시간 유효한 서명된 URL 생성
            meal_response = MealHourResponse_Full_Picture(
                id=meal.id,
                user_id=meal.user_id,
                daymeal_id=meal.daymeal_id,
                meal_time=meal.meal_time,
                name=meal.name,
                picture=meal.picture,
                text=meal.text,
                record_datetime=meal.record_datetime,
                heart=meal.heart,
                carb=meal.carb,
                protein=meal.protein,
                fat=meal.fat,
                calorie=meal.calorie,
                unit=meal.unit,
                size=meal.size,
                track_goal=meal.track_goal,
                label=meal.label,
                image_url=image_url
            )
            meals_with_url.append(meal_response)
        return meals_with_url

    def create_file_name(self, user_id: str):
        time = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"{user_id}_{time}"
        return filename

    def upload_temp(self, user_id: str, file: File(...)):
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

        # # Yolov 서버에서 반환된 정보  -->>>>>>>> label만 받는걸로 변경필요
        food_info = response.json()
        print(food_info)
        #food_info = {"is_success": True, "label": 14011001}
        is_success = bool(food_info.get("is_success", False))
        if is_success == False:
            temp_blob.delete()
            raise HTTPException(status_code=400, detail="No food data")
        return {"file_path": temp_blob.name, "food_info": food_info, "image_url": url}  ## 임시파일이름, food정보, url 반환

    def remove_temp_meal(self, file_path: Form):
        temp_blob = bucket.blob(file_path)

        if temp_blob.exists():
            temp_blob.delete()
            return {"detail": "Temporary file removed"}
        return {"detail": "No Temporary file here"}

    def register_mealhour(self, user_id: str, daytime: str, mealtime: MealTime,
                      hourminute: str, file_path: str, food_labels: str, text: str):

        try:
            # JSON 문자열을 Python 리스트로 변환
            food_labels_list = json.loads(food_labels)
            # 리스트 요소를 `int`로 변환
            food_labels_int = [int(label) for label in food_labels_list]
        except (json.JSONDecodeError, ValueError, TypeError):
            raise ErrorCode.INVALID_FORMAT  # JSON 변환 오류 발생 시 예외 처리
        record_date = self.invert_daytime_to_date(daytime)
        # hourminute 값을 받아 시간과 분으로 변환
        try:
            hour = int(hourminute[:2])
            minute = int(hourminute[2:])
        except (ValueError, IndexError):
            raise ErrorCode.INVALID_FORMAT
        mealhour_check = self.mealday_repo.find_mealhour_by_date(user_id=user_id, record_date=record_date, mealtime=mealtime)
        if mealhour_check:
            raise ErrorCode.MEALHOUR_EXIST

        temp_blob = bucket.blob(file_path)

        if not temp_blob.exists():
            raise ErrorCode.NO_TEMP_PICTURE

        # 임시 파일을 meal 폴더로 이동
        meal_blob = bucket.blob(f"meal/{os.path.basename(file_path)}")
        bucket.rename_blob(temp_blob, meal_blob.name)

        # 서명된 URL 생성
        signed_url = meal_blob.generate_signed_url(expiration=timedelta(hours=1))  # 60분
        print(signed_url)
        # 오늘 날짜와 hourminute를 결합한 datetime 객체 생성
        record_date_time = datetime.combine(record_date, time(hour, minute))

        for food_label in food_labels_int: #########-----> 현재 labels가 list[str]형태로 오고있어서 임시수정함 라벨온만큼 등록됨
            if self.mealday_repo.find_food(label=food_label) is None:
                meal_blob.delete()
                raise ErrorCode.NO_FOOD
            self.mealday_repo.create_mealhour(
                user_id=user_id,
                record_datetime=record_date_time,
                mealtime=mealtime,
                file_name=meal_blob.name,
                food_label=food_label,
                text=text
            )

        #self.mealday_repo.create_mealhour(user_id = user_id, record_datetime=record_date_time,
        #                                  mealtime=mealtime, file_name=meal_blob.name, food_label=food_label, text=text)

        ## 트랙 지킨 여부 아직 미완성
        # mentor_info = self.user_repo.find_users_mentor_info_by_user_id(user_id=user_id)
        # if mentor_info:
        #     data = {
        #         "user_id": user_id,
        #         "mentor_id": mentor_info["mentor_user_id"],
        #         "message": f"{mentor_info['username']}님이 {mealtime}을 등록했습니다."
        #     }
        #     send_fcm_data_noti(mentor_info["mentor_user_id"], "회원식사등록", data["message"], data)

    def remove_meal(self, user_id: str, daytime: str, mealtime: MealTime):
        record_date = self.invert_daytime_to_date(daytime)
        picture_path = self.mealday_repo.delete_mealhour(user_id = user_id, record_date = record_date, mealtime = mealtime)
        if picture_path is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        else:
            blob = bucket.blob(picture_path)
            if blob.exists():
                blob.delete()

    def apply_update_mealhour(self, mealhour, body: UpdateMealHourBody):
        """사용자 정보 업데이트 적용"""
        if body.heart is not None:
            mealhour.heart = body.heart
        if body.track_goal is not None:
            mealhour.track_goal = body.track_goal
        if body.size and body.size > 0:
            old_size = mealhour.size
            new_size = body.size
            percent = new_size / old_size if old_size > 0 else 1
            mealhour.size = new_size
            mealhour.carb *= percent
            mealhour.protein *= percent
            mealhour.fat *= percent
            mealhour.calorie *= percent
            return percent
        return 0

    def update_mealhour(self, user_id: str, daytime: str, mealtime:MealTime, body: UpdateMealHourBody):
        record_date = self.invert_daytime_to_date(daytime)
        mealhour = self.mealday_repo.find_mealhour_by_date(user_id=user_id,record_date=record_date,mealtime=mealtime)
        if mealhour is None:
            raise raise_error(ErrorCode.MEALHOUR_NOT_FOUND)
        percent = self.apply_update_mealhour(mealhour, body) ## 1이면 size변경, 0이면 size변경 X
        return self.mealday_repo.update_mealhour(mealhour, percent)