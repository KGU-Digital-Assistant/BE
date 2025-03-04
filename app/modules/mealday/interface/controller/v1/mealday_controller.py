from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, Query, Path

from typing import List
from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from containers import Container
from core.auth import CurrentUser, get_current_user
from database import get_db
from modules.mealday.application.mealday_service import MealDayService
from modules.mealday.domain.mealday import MealDay
from modules.mealday.interface.schema.mealday_schema import CreateMealDayBody,MealDayResponse_Date, MealDayResponse_Full,\
    MealDayResponse_Nutrient, MealDayResponse_Cheating, MealDayResponse_WCA, MealDayResponse_Calorie, MealDayResponse_TodayCalorie,\
    MealDayResponse_RecordCount, MealDayResponse_Avg_Calorie, UpdateMealDayBody
from utils.responses.response import APIResponse

router = APIRouter(prefix="/meal_day", tags=["mealday"])


@router.post("/post/meal_day/{daytime}", response_model=MealDayResponse_Date)
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

@router.post("/post/meal_day/{year}/{month}", response_model=APIResponse)
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
    return mealday_service.create_mealday_by_month(current_user.id,year,month)

@router.get("/get/mealday/{user_id}/{daytime}", response_model=MealDayResponse_Full)
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

@router.get("/get_mealday", response_model=MealDayResponse_Full)
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


@router.get("/get/goal_now_nutrient/{daytime}", response_model=MealDayResponse_Nutrient)
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

@router.get("/get/cheating/{daytime}", response_model=MealDayResponse_Cheating)
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

@router.get("/get/wca/mine/{daytime}", response_model=MealDayResponse_WCA)
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

@router.get("/get/wca/formentor/{user_id}/{daytime}", response_model=MealDayResponse_WCA)
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

@router.get("/get/calorie/{daytime}", response_model=MealDayResponse_Calorie)
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

@router.get("/get/calorie_today/{daytime}", response_model=MealDayResponse_TodayCalorie)
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

@router.get("/get/meal_recording_count/{year}/{month}", response_model=MealDayResponse_RecordCount)
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

@router.get("/get/meal_avg_calorie/{year}/{month}", response_model=MealDayResponse_Avg_Calorie)
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

@router.get("/get/calender/{user_id}", response_model=List[MealDayResponse_Full])
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

@router.patch("/update/weight/{daytime}/{weight}", response_model=APIResponse)
@inject
def update_weight(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    weight: Annotated[float, Path(description="몸무게 (형식: 15.7)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) 몸무게 업뎃 :
     - 입력예시 : daytime = 2024-06-01,weight = 15.2
    """
    body: UpdateMealDayBody = UpdateMealDayBody(
        weight=weight,
    )
    mealday_service.update_mealday(current_user.id, daytime, body)
    return APIResponse(status_code=status.HTTP_200_OK, message="Weight updated")
@router.patch("/update/burncaloire/{daytime}/{burncalorie}", response_model=APIResponse)
@inject
def update_burncalorie(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    burncalorie: Annotated[float, Path(description="소모칼로리 (형식: 15.7)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) 소모칼로리 업뎃 :
     - 입력예시 : daytime = 2024-06-01, burncalorie = 15.2
    """
    body: UpdateMealDayBody = UpdateMealDayBody(
        burncalorie=burncalorie,
    )
    mealday_service.update_mealday(current_user.id, daytime, body)
    return APIResponse(status_code=status.HTTP_200_OK, message="Burncalorie updated")

@router.patch("/update/wca/{daytime}", response_model=APIResponse)
@inject
def update_burncalorie(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
    body: UpdateMealDayBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) wca 업뎃 :
     - 입력예시 : daytime = 2024-06-01, Json{water=1, coffee=2, alcohol = 5}
    """
    mealday_service.update_mealday(current_user.id, daytime, body)
    return APIResponse(status_code=status.HTTP_200_OK, message="WCA updated")
