from typing import Annotated
from datetime import date
import json
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File, Form
from typing import List
from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from containers import Container
from core.auth import CurrentUser, get_current_user
from modules.mealday.application.mealday_service import MealDayService
from modules.mealday.interface.schema.mealday_schema import MealDayResponse_Date, MealDayResponse_Full,\
    MealDayResponse_Nutrient, MealDayResponse_Cheating, MealDayResponse_WCA, MealDayResponse_Calorie, MealDayResponse_TodayCalorie,\
    MealDayResponse_RecordCount, UpdateMealDayBody, MealHourResponse_Full, UpdateMealHourBody, MealHourResponse_Full_Picture
from utils.responses.response import APIResponse

mealday_router = APIRouter(prefix="/api/v1/meal_day", tags=["mealday"])


@mealday_router.post("/post/{daytime}", response_model=MealDayResponse_Date)
@inject
def create_mealday_by_date(
        daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
    식단일일(MealDay) db생성 : 앱실행시(당일날짜로), track시작시 해당기간에 생성
     - 입력예시 : daytime = 2024-06-01
    """
    return mealday_service.create_mealday_by_date(current_user.id,daytime)

@mealday_router.post("/post/{year}/{month}", response_model=APIResponse)
@inject
def create_mealday_by_month(
        year: Annotated[int, Path(description="생성년도 (형식: 2024)")],
        month: Annotated[int, Path(description="생성월 (형식: 06)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
    특정 월 동안의 식단일일(MealDay) db생성 : 앱실행시(해당월 입력) 해당기간에 생성
    - 입력예시 : year = 2024, month = 6
    """
    created_count = mealday_service.create_mealday_by_month(current_user.id,year,month)
    return APIResponse(status_code=status.HTTP_200_OK, message=f"{created_count}meal days created")

@mealday_router.get("/get/{user_id}/{daytime}", response_model=MealDayResponse_Full)
@inject
def get_mealday_by_date(
    user_id: Annotated[str, Path(description="유저id")],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) 전체 조회
     - 입력예시 : user_id = afdsttwssfa, daytime = 2024-06-01
    """
    return mealday_service.find_mealday_by_date(user_id,daytime)

@mealday_router.get("/get_mealday", response_model=MealDayResponse_Full)
@inject
def get_mealday_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    record_date: date = Query(..., description="조회할 날짜"),
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) 전체 조회
     - 입력예시 : daytime = 2024-06-01
    """
    return mealday_service.find_mealday_by_date(current_user.id, record_date)


@mealday_router.get("/get/goal_now_nutrient/{daytime}", response_model=MealDayResponse_Nutrient)
@inject
def get_mealday_nutrient_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    금일 탄단지, 목표 탄단지 출력
     - 입력예시 : daytime = 2024-06-01
     - 출력 : carb,protein,fat, gb_carb, gb_protein, gb_carb
    """
    return mealday_service.find_mealday_by_date(current_user.id, daytime)

@mealday_router.get("/get/cheating/{daytime}", response_model=MealDayResponse_Cheating)
@inject
def get_mealday_cheating_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    금일 Cheating 여부 출력
     - 입력예시 : daytime = 2024-06-01
     - 출력 : cheating(1 or 0)
    """
    return mealday_service.find_mealday_by_date(current_user.id, daytime)

@mealday_router.get("/get/wca/mine/{daytime}", response_model=MealDayResponse_WCA)
@inject
def get_mealday_wca_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) wca 조회
     - 입력예시 : daytime = 2024-06-01
     - 출력 : MealDay.water, MealDay.coffee, MealDay.alcohol
    """
    return mealday_service.find_mealday_by_date(current_user.id, daytime)

@mealday_router.get("/get/wca/formentor/{user_id}/{daytime}", response_model=MealDayResponse_WCA)
@inject
def get_mealday_wca_by_date(
    user_id: Annotated[str, Path(description="유저id")],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) wca 조회
     - 입력예시 : user_id = sa31dafe1, daytime = 2024-06-01
     - 출력 : MealDay.water, MealDay.coffee, MealDay.alcohol
    """
    return mealday_service.find_mealday_by_date(user_id, daytime)

@mealday_router.get("/get/calorie/{daytime}", response_model=MealDayResponse_Calorie)
@inject
def get_mealday_calorie_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) goal, now calorie
     - 입력예시 : daytime = 2024-06-01
     - 출력 : MealDay.goalcaloire, MealDay.nowcaloire
    """
    return mealday_service.find_mealday_by_date(current_user.id, daytime)

@mealday_router.get("/get/calorie_today/{daytime}", response_model=MealDayResponse_TodayCalorie)
@inject
def get_mealday_todaycalorie_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    금일 칼로리, 목표칼로리 조회, 섭취칼로리, 소모칼로리, 몸무게 조회
     - 입력예시 : 2024-06-01
     - 출력 : todaycalorie(nowcalorie - burncalorie), MealDay.goalcaloire,
             MealDay.nowcalorie, MealDay.burncalorie. MealDay.weight

    """
    return mealday_service.find_mealday_todaycalorie_by_date(current_user.id, daytime)

@mealday_router.get("/get/meal_recording_count/{year}/{month}", response_model=MealDayResponse_RecordCount)
@inject
def get_meal_record_count(
        year: Annotated[int, Path(description="생성년도 (형식: 2024)")],
        month: Annotated[int, Path(description="생성월 (형식: 06)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
        특정 월 동안의 식단게시수 조회
        - 입력예시 : year = 2024, month = 6
        - 출력 : 식단기록일 / 해당월의 총 일수
    """
    return mealday_service.get_mealday_record_count_by_date(current_user.id,year,month)

@mealday_router.get("/get/meal_avg_calorie/{year}/{month}", response_model=MealDayResponse_RecordCount)
@inject
def get_meal_avg_calorie(
        year: Annotated[int, Path(description="생성년도 (형식: 2024)")],
        month: Annotated[int, Path(description="생성월 (형식: 06)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
        특정 월 동안의 일 평균 칼로리 조회
        - 입력예시 : year = 2024, month = 6
        - 출력 : 식단기록일 / 해당월의 총 일수
    """
    return mealday_service.get_mealday_avg_calorie(current_user.id,year,month)

@mealday_router.get("/get/calender/{user_id}", response_model=List[MealDayResponse_Full])
@inject
def get_calendar(
        user_id: Annotated[str, Path(description="유저id")],
        year: Annotated[int, Query(description="생성년도 (형식: 2024)")],
        month: Annotated[int, Query(description="생성월 (형식: 06)")],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
    user_id와 month 정보를 넘기면 해당 월에 식단 정보 날짜 순으로 반환
    """
    return mealday_service.get_meal_list(user_id,year,month)

@mealday_router.patch("/update/{daytime}/{weight}", response_model=APIResponse)
@inject
def update_mealday(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    body: UpdateMealDayBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) 몸무게 업뎃 :
     - 입력예시 : daytime = 2024-06-01, body = {weight: 45.2} / {burncalorie: 15.2}/ {water=1, coffee=2, alcohol = 5}
    """
    mealday_service.update_mealday(current_user.id, daytime, body)
    return APIResponse(status_code=status.HTTP_200_OK, message="Mealhour updated")

########################################################################
##############MealHour##################################################
########################################################################'

mealhour_router = APIRouter(prefix="/api/v1/meal_hour", tags=["mealhour"])

@mealhour_router.get("/get/mine/{mealhour_id}", response_model=MealHourResponse_Full)
@inject
def get_mealhour_by_id(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    mealhour_id: Annotated[str, Path(description=" (형식: dfasewrwea)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 전체 Column 조회
     - 입력예시 : id = dsafeawfwa
    """
    return mealday_service.get_mealhour_by_id(current_user.id, mealhour_id)
@mealhour_router.get("/get/mine/{daytime}/{mealtime}", response_model=MealHourResponse_Full)
@inject
def get_mealhour_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 전체 Column 조회
     - 입력예시 : daytime = 2024-06-01 / mealtime = LUNCH
    """
    return mealday_service.get_mealhour_by_date(current_user.id, daytime, mealtime)

@mealhour_router.get("/get/formentor/{user_id}/{daytime}/{mealtime}", response_model=MealHourResponse_Full)
@inject
def get_mealhour_by_date(
    user_id: Annotated[str, Path(description=" (형식: 유저id)")],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 전체 Column 조회
     - 입력예시 : user_id = dafdafewreta ,daytime = 2024-06-01 / mealtime = LUNCH
    """
    return mealday_service.get_mealhour_by_date(user_id, daytime, mealtime)

@mealhour_router.get("/get_mealhour_picture/mine/{daytime}/{mealtime}")
@inject
async def get_mealhour_picture(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 사진 조회
     - 입력예시 : daytime = 2024-06-01 / mealtime = LUNCH
     - 출력 : image_url
    """
    return mealday_service.get_mealhour_picture(current_user.id, daytime, mealtime)

@mealhour_router.get("/get_mealhour_picture/formentor/{user_id}/{daytime}/{mealtime}")
@inject
async def get_mealhour_picture(
    user_id: Annotated[str, Path(description=" (형식: 유저id)")],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 사진 조회
     - 입력예시 : user_id = afdawetatewa, daytime = 2024-06-01 / mealtime = LUNCH
     - 출력 : image_url
    """
    return mealday_service.get_mealhour_picture(user_id, daytime, mealtime)

@mealhour_router.get("/get/daymeal/{daytime}", response_model=List[MealHourResponse_Full_Picture])
@inject
def get_mealhour_date_all(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    해당일 등록 식단 전체 출력
     - 입력예시 : daytime = 2024-06-01
     - 출력 : 당일 식단게시글[MealHour.time, MealHour.name]
    """
    return mealday_service.get_mealhour_by_date_all(current_user.id, daytime)

@mealhour_router.get("/get/daymeal/formentor/{user_id}/{daytime}", response_model=List[MealHourResponse_Full_Picture])
@inject
def get_mealhour_date_all(
    user_id: Annotated[str, Path(description=" (형식: dafdsa)")],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    해당일 등록 식단 전체 출력
     - 입력예시 : daytime = 2024-06-01
     - 출력 : 당일 식단게시글[MealHour.time, MealHour.name]
    """
    return mealday_service.get_mealhour_by_date_all(user_id, daytime)

@mealhour_router.post("/upload_temp") ## 임시로 파일을 firebase저장하고 yolo서버로 전송
@inject
async def upload_food(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    file: Annotated[UploadFile, File((...),description="사진파일")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 사진 입력시 firebase에 임시저장 및 yolo서버로부터 food정보 Get : 10page 2번
     - 입력예시 : 사진파일
     - 출력 : file_path, food_info, image_url
    """
    return mealday_service.upload_temp(current_user.id, file)

@mealhour_router.post("/remove_temp_meal") ##식단게시 취소시 임시파일삭제(임시저장사진명 필요:file_path)
@inject
async def remove_temp_meal(
    file_path: Annotated[str, Form(..., description="upload_temp로 얻은 file_path")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 식단등록시 뒤로가기를 통한 임시저장된 음식사진삭제 : 10page 4-2번(뒤로가기)
     - 입력예시 : file_path (meal_hour/upload_temp api로 얻은 임시 파일경로)
    """
    return mealday_service.remove_temp_meal(file_path)


@mealhour_router.post("/register_meal/{daytime}/{mealtime}/{hourminute}", response_model=APIResponse) ## 등록시 임시업로드에 사용한데이터 입력필요 (임시사진이름file_path, food_info, text)
@inject
async def register_meal(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    hourminute: Annotated[str, Path(description=" (형식: 0610)")],
    file_path: Annotated[str, Form(..., description="upload_temp로 얻은 file_path")],
    labels: Annotated[str, Form(..., description="upload_temp로 얻은 food_info의 labels")],  # ✅ `List[str]`
    text: Annotated[str, Form(description="내용 작성")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 등록 (/meal_hour/upload_temp api로 얻은 data 활용
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH, hourminute = 0610, file_path, food_label, text = 오늘점심등록햇당
    """
    mealday_service.register_mealhour(current_user.id, daytime, mealtime, hourminute, file_path, labels, text)
    return APIResponse(status_code=status.HTTP_200_OK, message="Mealhour Post Success")

@mealhour_router.post("/remove_meal/{daytime}/{mealtime}", response_model=APIResponse) ## 등록한 mealhour 삭제
@inject
async def remove_meal(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 삭제
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH
    """
    mealday_service.remove_meal(current_user.id, daytime, mealtime)
    return APIResponse(status_code=status.HTTP_200_OK, message="Mealhour Delete Success")


@mealhour_router.patch("/update/{daytime}/{mealtime}", response_model=APIResponse)
@inject
def update_mealhour(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    body: UpdateMealHourBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간 size 변경-> 먹은 음식 gram 수 변경
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH, size = 105.2, body ={track_goal: true} / {
                                                                       {heart: true}/ {size: 200}
    """
    mealday_service.update_mealhour(current_user.id, daytime, mealtime, body)

    return APIResponse(status_code=status.HTTP_200_OK, message="Mealhour Update Success")

@mealhour_router.patch("/update/formentor/{user_id}/{daytime}/{mealtime}", response_model=APIResponse)
@inject
def update_mealhour(
    user_id: Annotated[str, Path(description=" (형식: Dsdfsadf)")],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    body: UpdateMealHourBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간 size 변경-> 먹은 음식 gram 수 변경
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH, size = 105.2, body ={track_goal: true} / {
                                                                       {heart: true}/ {size: 200}
    """
    mealday_service.update_mealhour(user_id, daytime, mealtime, body)

    return APIResponse(status_code=status.HTTP_200_OK, message="Mealhour Update Success")