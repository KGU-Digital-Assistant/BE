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
from utils.parser import weekday_parse, time_parse, mealtime_parse

from core.fcm import send_fcm_data_noti
from modules.user.application.user_service import UserService
from modules.mealday.domain.repository.mealday_repo import IMealDayRepository
from modules.track.application.track_service import TrackService
from modules.food.application.food_service import FoodService
from modules.mealday.domain.mealday import MealDay as MealDayV0
from modules.track.interface.schema.track_schema import MealTime
from modules.mealday.interface.schema.mealday_schema import CreateDishBody, MealDayResponse_Full, \
    UpdateMealDayBody, UpdateDishBody, DishImageUrl, DishResponse, DishGroupResponse
from utils.crypto import Crypto
from utils.db_utils import orm_to_pydantic, dataclass_to_pydantic
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error

class MealDayService:
    @inject
    def __init__(
            self,
            mealday_repo: IMealDayRepository,
            user_service: UserService,
            track_service: TrackService,
            food_service: FoodService,
            crypto: Crypto,
    ):
        self.mealday_repo = mealday_repo
        self.user_servcie = user_service
        self.track_service = track_service
        self.food_service = food_service
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

    def create_mealday_by_track_id(self, user_id: str, track_id: str):
        track = self.track_service.validate_track(track_id=track_id, user_id=user_id)
        if track is None:
            raise raise_error(ErrorCode.TRACK_NOT_FOUND)
        count = self.mealday_repo.save_many_mealday(user_id = user_id, track_id=track_id, first_day=track.start_date, last_day = track.finish_date)
        return count

    def find_mealday_by_date(self, user_id: str, daytime: str):
        record_date = self.invert_daytime_to_date(daytime)
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
############## 무스 ##################################################
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

########################################################################
############## Dish ##################################################
########################################################################

    def register_dish_v1(self, user_id: str, daytime: str, routine_id: str):
        record_date = self.invert_daytime_to_date(daytime)
        track_routine_foods = self.track_service.get_routine_food_all_by_routine_id(routine_id=routine_id)
        mealday = self.mealday_repo.find_by_date(user_id=user_id,record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        track_part = self.track_service.get_track_part_by_user_track_id(user_id=user_id, track_id=mealday.track_id)
        for track_routine in track_routine_foods:
            for rf in track_routine.routine_foods:
                routine_food_check = self.track_service.get_routine_food_check_by_routine_food_id(routine_food_id=rf.id, user_id=user_id)
                if routine_food_check:
                    raise raise_error(ErrorCode.DISH_ALREADY_EXIST)
                image_path = None
                label = rf.food_label if rf.food_label is not None else None
                if rf.food_label is not None and rf.food is not None:
                    file_id = self.create_file_name(user_id=user_id)
                    dish_path = f"meal/{file_id}"
                    food_blob = bucket.blob(rf.food.image_url if rf.food.image_url is not None else dish_path)
                    dish_blob = bucket.blob(dish_path)
                    bucket.copy_blob(food_blob, bucket, dish_blob.name)
                    image_path = dish_blob.name
                dish = self.mealday_repo.create_dish_trackroutine(user_id=user_id, mealday_id=mealday.id, trackroutine=track_routine,
                                                                  trackpart_id=track_part.id, image_url=image_path, quantity=rf.quantity, food=rf.food, label=label, name=rf.food_name)
                self.track_service.create_routine_food_check(routine_food_id=rf.id, dish_id=dish.id, user_id=user_id)
                self.track_service.update_routine_check(user_id=user_id,routine_id=routine_id, status=True)

    def register_dish_v2(self, user_id: str, daytime: str, routine_food_id: str, picture: UploadFile = File(...)):
        record_date = self.invert_daytime_to_date(daytime)
        routine_food_check = self.track_service.get_routine_food_check_by_routine_food_id(routine_food_id=routine_food_id,
                                                                                          user_id=user_id)
        if routine_food_check:
            raise raise_error(ErrorCode.DISH_ALREADY_EXIST)
        routine_food = self.track_service.get_routine_food_by_id(routine_food_id=routine_food_id, user_id=user_id)
        track_routine = self.track_service.get_routine_by_id(routine_id=routine_food.routine_id, user_id=user_id)
        mealday = self.mealday_repo.find_by_date(user_id=user_id,record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)

        track_part = self.track_service.get_track_part_by_user_track_id(user_id=user_id, track_id=mealday.track_id)
        file_id = self.create_file_name(user_id=user_id)
        blob = bucket.blob(f"meal/{file_id}")
        blob.upload_from_file(picture.file, content_type=picture.content_type)
        image_path = blob.name
        dish = self.mealday_repo.create_dish_trackroutine(user_id=user_id, mealday_id=mealday.id, trackroutine=track_routine,
                                                          trackpart_id=track_part.id, image_url=image_path, quantity=routine_food.quantity,food=None, label=None, name=routine_food.food_name)
        self.track_service.create_routine_food_check(routine_food_id=routine_food_id, dish_id=dish.id, user_id=user_id)
        self.track_service.update_routine_check(user_id=user_id,routine_id=track_routine.id, status=True)


    def register_dish_v3(self, user_id: str, daytime: str, routine_food_ids: List[str]):
        record_date = self.invert_daytime_to_date(daytime)
        mealday = self.mealday_repo.find_by_date(user_id=user_id,record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        track_part = self.track_service.get_track_part_by_user_track_id(user_id=user_id, track_id=mealday.track_id)
        for routine_food_id in routine_food_ids:
            routine_food_check = self.track_service.get_routine_food_check_by_routine_food_id(routine_food_id=routine_food_id,
                                                                                              user_id=user_id)
            if routine_food_check:
                raise raise_error(ErrorCode.DISH_ALREADY_EXIST)
            routine_food = self.track_service.get_routine_food_with_food_by_id(routine_food_id=routine_food_id)
            track_routine = self.track_service.get_routine_by_id(routine_id=routine_food.routine_id, user_id=user_id)
            image_path = None
            label = routine_food.food_label if routine_food.food_label is not None else None
            if routine_food.food_label is not None and routine_food.food is not None:
                file_id = self.create_file_name(user_id=user_id)
                dish_path = f"meal/{file_id}"
                food_blob = bucket.blob(routine_food.food.image_url)
                dish_blob = bucket.blob(dish_path)
                bucket.copy_blob(food_blob, bucket, dish_blob.name)
                image_path = dish_blob.name
            dish = self.mealday_repo.create_dish_trackroutine(user_id=user_id, mealday_id=mealday.id, trackroutine=track_routine,
                                                              trackpart_id=track_part.id, image_url=image_path, quantity=routine_food.quantity,food=routine_food.food, label=label, name=routine_food.food_name)
            self.track_service.create_routine_food_check(routine_food_id=routine_food.id, dish_id=dish.id,
                                                                           user_id=user_id)
            self.track_service.update_routine_check(user_id=user_id,routine_id=track_routine.id, status=True)

    def register_dish_v4(self, user_id: str, daytime: str, body: CreateDishBody):
        record_date = self.invert_daytime_to_date(daytime)
        mealday = self.mealday_repo.find_by_date(user_id=user_id,record_date=record_date)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        trackpart = self.track_service.get_track_part_by_user_track_id(user_id=user_id, track_id=mealday.track_id)
        food = None
        image_path = None
        if body.label is not None:
            food = self.food_service.get_food_data(food_label=body.label)
            if food is None:
                raise raise_error(ErrorCode.NO_FOOD)
            mealtime = time_parse(body.mealtime)
            file_id = self.create_file_name(user_id=user_id)
            dish_path = f"meal/{file_id}"
            food_blob = bucket.blob(food.image_url)
            dish_blob = bucket.blob(dish_path)
            bucket.copy_blob(food_blob, bucket, dish_blob.name)
            image_path = dish_blob.name
        self.mealday_repo.create_dish(user_id=user_id, mealday_id=mealday.id, body=body,
            trackpart_id=trackpart.id, mealtime = mealtime,food = food, image_path=image_path)


    def find_dish(self, user_id: str, dish_id: str):
        dish = self.mealday_repo.find_dish(user_id= user_id, dish_id= dish_id)
        if dish is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        if dish.image_url and dish.image_url is not None:
            try:
                # 서명된 URL 생성 (URL은 1시간 동안 유효)
                blob = bucket.blob(dish.image_url)
                signed_url = blob.generate_signed_url(expiration=timedelta(hours=1))
            except Exception:
                raise raise_error(ErrorCode.DISH_NOT_FOUND)
            dish.image_url = signed_url
        return dish

    def get_dish_not_routine(self, user_id: str, track_id: str):
        track = self.track_service.validate_track(track_id=track_id, user_id=user_id)
        start_date = track.start_date
        finish_date = track.finish_date
        group_list = []
        num = 1
        while finish_date >= start_date:
            mealday = self.mealday_repo.find_by_date(user_id=user_id, record_date=start_date)
            if mealday is None:
                raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
            all_dishes = self.mealday_repo.find_dish_all(mealday_id=mealday.id,user_id=user_id)
            dishes_list=[]
            for dish in all_dishes:
                routine_food_check = self.track_service.get_routine_food_check_by_dish_id(dish_id=dish.id,user_id=user_id)
                if routine_food_check:
                    continue
                else:
                    image_url = None
                    if dish.image_url:
                        dish_blob = bucket.blob(dish.image_url)
                        image_url = dish_blob.generate_signed_url(expiration=timedelta(hours=1))  # 60분 유효url
                    dish_response = DishResponse(
                        id = dish.id,
                        mealtime = dish.mealtime,
                        label = dish.label,
                        name = dish.name,
                        quantity = dish.quantity,
                        calorie = dish.calorie,
                        image_url = image_url
                    )
                    dishes_list.append(dish_response)
                dishes_list = sorted(dishes_list, key=lambda dish: mealtime_parse(dish.mealtime))
            dish_group_response = DishGroupResponse(
                record_date = start_date,
                days= num,
                total_calorie = mealday.nowcalorie,
                dishes = dishes_list
            )
            group_list.append(dish_group_response)
            start_date += timedelta(days=1)
        return group_list

    def remove_dish(self, user_id: str, dish_id: str):
        dish = self.mealday_repo.find_dish(user_id=user_id,dish_id=dish_id)
        if dish is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        routine_food_check = self.track_service.get_routine_food_check_by_dish_id(dish_id=dish_id, user_id=user_id) #삭제할 dish의 루틴푸드체크
        ## 루틴을 지킨 dish를 삭제하는 경우
        if routine_food_check: ##
            routine_food_id = routine_food_check.routine_food_id  # 루틴 푸드 id 저장
            self.track_service.delete_routine_food_check_by_dish_id(dish_id=dish_id,user_id=user_id) #삭제할 dish의 루틴푸드체크 삭제
            routine_food = self.track_service.get_routine_food_by_id(routine_food_id=routine_food_id, user_id=user_id) #루틴푸드 조회
            routine_food_all = self.track_service.get_routine_food_all_by_routine_id(routine_id=routine_food.routine_id) #루틴id가 같은 모든 루틴푸드조회
            num = 0
            for trackroutine in routine_food_all:  # 루틴푸드들을 순회
                for food in trackroutine.routine_foods:
                    r_food_check = self.track_service.get_routine_food_check_by_routine_food_id(
                        routine_food_id=food.id, user_id=user_id)
                    print(f"루틴푸드ID: {food.id}, 루틴푸드체크 존재여부: {bool(r_food_check)}")
                    # 만약 각 루틴푸드 id에 맞는 루틴푸드체크의 존재여부를 확인
                    if r_food_check:
                        num += 1
            print(f"남은 총 루틴푸드 갯수: {num}")
            if num < 1:
                #만약 루틴푸드체크가 없다면 삭제한 dish 이외에 루틴푸드를 지킨 식단이 없으므로 루틴체크를 false로 변경
                self.track_service.update_routine_check(user_id=user_id, routine_id=routine_food.routine_id,
                                                        status=False)
        image_url = self.mealday_repo.delete_dish(user_id = user_id, dish_id = dish_id)
        if image_url is None:
            return
        else:
            blob = bucket.blob(image_url)
            if blob.exists():
                blob.delete()

    def apply_update_dish(self, dish, body: UpdateDishBody, status: int):
        """사용자 정보 업데이트 적용"""
        if body.heart is not None:
            dish.heart = body.heart
        if body.track_goal is not None:
            dish.track_goal = body.track_goal
        if body.quantity and body.quantity > 0 and status == 1:
            old_quantity = dish.quantity
            new_quantity = body.quantity
            percent = new_quantity / old_quantity if old_quantity > 0 else 1
            dish.quantity = new_quantity
            dish.carb *= percent
            dish.protein *= percent
            dish.fat *= percent
            dish.calorie *= percent
            return percent
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
        dish = self.mealday_repo.find_dish(user_id=user_id, dish_id=dish_id)
        if dish is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        food_info = self.food_service.get_food_data(body.label)
        if food_info is None and body.label:
            raise raise_error(ErrorCode.NO_FOOD)
        ### 수량만 변화 -> label 혹은 name은 dish와 같은 내용일 경우
        if (dish.name == body.name and dish.label is None) or (dish.label == body.label and body.name is None):
            percent = self.apply_update_dish(dish, body, 1) ## 1이면 size변경, 0이면 size변경 X
            new_dish = self.mealday_repo.update_dish(dish, percent, dish.image_url)
            return new_dish

        target_label = body.label
        target_name = body.name

        # 현재 dish와 연결된 routine_food_check
        current_rf_check = self.track_service.get_routine_food_check_by_dish_id(dish_id, user_id)
        # routine_food 조회릘 위한 routine찾기
        mealday = self.mealday_repo.find_by_id(mealday_id=dish.mealday_id)
        if mealday is None:
            raise raise_error(ErrorCode.MEALDAY_NOT_FOUND)
        routine = self.track_service.get_routine_by_days_mealtime(track_id=mealday.track_id, days=dish.days,mealtime=dish.mealtime)
        # 1) 같은 label/name을 가진 routine_food 찾기
        routine_food = self.track_service.find_routine_food_by_label_or_name_with_routine_id(
            routine_id=routine.id,
            label=target_label,
            name=target_name
        )
        print(f"routine_food: {bool(routine_food)}", flush=True)
        if routine_food:
            # 1-1) routine_food_check가 있는 경우: dish 수량 증가
            target_rf_check = self.track_service.get_routine_food_check_by_routine_food_id(
                routine_food_id=routine_food.id, user_id=user_id
            )
            if target_rf_check:
                new_dish = self.mealday_repo.update_dish_quantity(
                    dish_id=target_rf_check.dish_id,
                    quantity=body.quantity,
                    food=food_info,
                    name=body.name
                )
                # 현재 dish 삭제 및 routine_food_check 삭제
                if current_rf_check:
                    self.track_service.delete_routine_food_check_by_dish_id(dish_id, user_id)
                self.mealday_repo.delete_dish(user_id=user_id, dish_id=dish_id)
                return new_dish
            else:
                # 1-2) routine_food_check가 없는 경우: dish 수정 + routine_food_check 생성
                new_dish = self.mealday_repo.update_dish_label_or_name(
                    dish_id=dish_id,
                    name=target_name,
                    quantity=body.quantity,
                    food=food_info
                )
                if current_rf_check:
                    self.track_service.delete_routine_food_check_by_dish_id(dish_id, user_id)

                self.track_service.create_routine_food_check(
                    routine_food_id=routine_food.id, dish_id=dish_id, user_id=user_id
                )
                self.track_service.update_routine_check(
                    user_id=user_id, routine_id=routine.id, status=True
                )
                return new_dish
        else:
            # 2) routine_food에 해당 label/name이 없는 경우: dish 수정
            new_dish = self.mealday_repo.update_dish_label_or_name(
                dish_id=dish_id,
                name=target_name,
                quantity=body.quantity,
                food=food_info
            )
            # 기존 routine_food_check 삭제 및 routine_check status 업데이트
            if current_rf_check:
                self.track_service.delete_routine_food_check_by_dish_id(dish_id, user_id)
                remain = self.track_service.count_routine_food_checks_by_routine_food_id(
                    routine_id=routine.id, user_id=user_id)
                if remain == 0:
                    self.track_service.update_routine_check(
                        user_id=user_id, routine_id=routine.id, status=False
                    )
            return new_dish

    def update_dish_image(self, user_id: str, dish_id: str):
        dish = self.mealday_repo.find_dish(user_id=user_id, dish_id=dish_id)
        if dish is None:
            raise raise_error(ErrorCode.DISH_NOT_FOUND)
        food = self.food_service.get_food_data(dish.label)
        if food is None:
            raise raise_error(ErrorCode.NO_FOOD)
        file_id = self.create_file_name(user_id=user_id)
        dish_path = f"meal/{file_id}"
        food_blob = bucket.blob(food.image_url)
        dish_blob = bucket.blob(dish_path)
        bucket.copy_blob(food_blob, bucket, dish_blob.name)
        image_path = dish_blob.name
        self.mealday_repo.update_dish_image(dish.id, image_path)
        url = dish_blob.generate_signed_url(expiration=timedelta(hours=1))  # 60분 유효url
        return DishImageUrl(image_url=url)