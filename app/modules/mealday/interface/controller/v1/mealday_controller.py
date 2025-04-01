from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File, Form
from typing import List, Optional
from dependency_injector.wiring import inject, Provide
from starlette import status
from containers import Container
from core.auth import CurrentUser, get_current_user
from modules.mealday.application.mealday_service import MealDayService
from modules.mealday.interface.schema.mealday_schema import MealDayResponse_Date, MealDayResponse_Full,\
    Dish_Full,UpdateDishBody, Food_Data, Dish_with_datetime
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

@mealday_router.post("/post/{track_id}", response_model=APIResponse)
@inject
def create_mealday_by_track_id(
        track_id: Annotated[str, Path(description="트랙 id (형식: dasfdsafads)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
    특정 트랙 사용기간 동안의 MealDay db생성 : 앱실행시(해당월 입력) 해당기간에 생성
     - 트랙 시작하기누를때 이거 먼저 만들어야함
    - 입력예시 : track_id =f dasfdsf
    """
    created_count = mealday_service.create_mealday_track_id(current_user.id, track_id)
    return APIResponse(status_code=status.HTTP_200_OK, message=f"{created_count}meal days created")

@mealday_router.get("/get", response_model=MealDayResponse_Full)
@inject
def get_mealday_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    record_date: date = Query(..., description="조회할 날짜"),
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단일일(MealDay) 전체 조회
     - 입력예시 : daytime = 2024-06-01
     - 기능명세서 v1-7-1
    """
    return mealday_service.find_mealday_by_date(current_user.id, record_date)

@mealday_router.post("/moose")
@inject
async def moose(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    file: Annotated[UploadFile, File((...),description="사진파일")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 사진 입력시 firebase에 임시저장 및 yolo서버로부터 food정보 Get : 10page 2번
     - 입력예시 : 사진파일
     - 출력 : file_path, food_info, image_url
    """
    return mealday_service.moose(current_user.id, file)

@mealday_router.post("/remove_moose") ##식단게시 취소시 임시파일삭제(임시저장사진명 필요:file_path)
@inject
async def remove_moose(
    file_path: Annotated[str, Form(..., description="moose로 얻은 file_path")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 식단등록시 뒤로가기를 통한 임시저장된 음식사진삭제 : 10page 4-2번(뒤로가기)
     - 입력예시 : file_path (moose api로 얻은 임시 파일경로)
    """
    return mealday_service.remove_moose(file_path)

@mealday_router.get("/get_all_dishes/{track_id}", response_model=List[Dish_with_datetime])
@inject
def get_all_dishes_by_track_id(
        track_id: Annotated[str, Path(description="트랙 id (형식: dasfdsafads)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    return mealday_service.get_all_dishes_by_track_id(current_user.id, track_id)



@mealday_router.post("/dish/register", response_model=APIResponse)
@inject
async def register_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: YYYY-MM-DD)")],
    mealtime: Annotated[str, Path(description="시간대 (형식: LUNCH)")],
    name: Annotated[List[str], Form(..., description="음식 이름 리스트")],
    calorie: Annotated[List[float], Form(..., description="칼로리 리스트")],
    picture: Annotated[Optional[List[UploadFile]], File(None, description="사진 리스트. 비어도 OK")] = None,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 등록 (/dish/upload_temp api로 얻은 data 활용
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH, name = ["치킨", "피자"], calorie =[100, 200], picture=[사진파일 2개]
    """
    mealday_service.register_dish(current_user.id, daytime, mealtime, name, calorie, picture)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Post Success")

@mealday_router.get("/dish/get/{dish_id}", response_model=Dish_Full)
@inject
async def get_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 삭제
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH
    """
    return mealday_service.find_dish(current_user.id, dish_id)

@mealday_router.post("/dish/remove/{dish_id}", response_model=APIResponse) ## 등록한 Dish 삭제
@inject
async def remove_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간별(MealHour) 삭제
     - 입력예시 : daytime = 2024-06-01, mealtime = LUNCH
    """
    mealday_service.remove_dish(current_user.id, dish_id)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Delete Success")


@mealday_router.patch("/dish/update/{dish_id}", response_model=APIResponse)
@inject
def update_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    body: UpdateDishBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단시간 size 변경-> 먹은 음식 gram 수 변경
     - 입력예시 : dish_id = dsafeawewrqr, size = 105.2, body ={track_goal: true} / {
                                                                       {heart: true}/ {size: 200}
    """
    mealday_service.update_dish(current_user.id, dish_id, body)

    return APIResponse(status_code=status.HTTP_200_OK, message="Mealhour Update Success")

@mealday_router.get("/get/food_data", response_model=Food_Data)
@inject
def get_food_data(
    name: str = Query(..., description="조회할 음식명"),
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    음식명 입력후 칼로리 조회
    """
    return mealday_service.get_food_data(name)
