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
    Dish_Full,UpdateDishBody, UpdateMealDayBody, CreateDishBody, DishImageUrl, DishGroupResponse
from utils.responses.response import APIResponse


mealday_router = APIRouter(prefix="/api/v1/meal_day", tags=["mealday"])


@mealday_router.post("/date/{daytime}", response_model=MealDayResponse_Date)
@inject
def create_mealday_by_date(
        daytime: Annotated[str, Path(description="생성날짜 (형식: YYYY-MM-DD)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
    MealDay db생성 : 앱실행시(당일날짜로), track시작시 해당기간에 생성
     - 입력예시 : daytime = 2024-06-01
    """
    return mealday_service.create_mealday_by_date(current_user.id,daytime)

@mealday_router.post("/track_id/{track_id}", response_model=APIResponse)
@inject
def create_mealday_by_track_id(
        track_id: Annotated[str, Path(description="트랙 id (형식: dasfdsafads)")],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service])):
    """
    특정 트랙 사용기간 동안의 MealDay db생성 : 앱실행시(해당월 입력) 해당기간에 생성
     - 트랙 시작하기누를때 이거 먼저 만들어야함
     - 입력예시 : track_id =f dasfdsf
     - 기능명세서 :
    """
    created_count = mealday_service.create_mealday_by_track_id(current_user.id, track_id)
    return APIResponse(status_code=status.HTTP_200_OK, message=f"{created_count} mealday created")

@mealday_router.get("/{daytime}", response_model=MealDayResponse_Full)
@inject
def get_mealday_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="기록일자 (형식: 2024-06-01)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    MealDay 전체 조회
     - 입력예시 : daytime = 2024-06-01
     - 출력 : MealDay 전체 Column
     - 기능명세서 : v1-7-1
    """
    return mealday_service.find_mealday_by_date(current_user.id, daytime)

@mealday_router.patch("/{daytime}", response_model=APIResponse)
@inject
def update_mealday(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description=" (형식: 기록날짜)")],
    body: UpdateMealDayBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    Mealday의 weight, burncalorie, water, coffe, alcohol 등으 변경
     - 입력예시 : daytime = 2024-06-01, body ={weight: 50.4}
    """
    mealday_service.update_mealday(current_user.id, daytime, body)

    return APIResponse(status_code=status.HTTP_200_OK, message="MealDay Update Success")


######################################## 무스 ########################################

@mealday_router.post("/moose")
@inject
async def moose(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    file: Annotated[UploadFile, File((...),description="사진파일")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    사진입력시 해당 사진 moose 제공
     - 입력예시 : 사진파일
     - 출력 : file_path, food_info, image_url
     - 기능명세서 :
    """
    return mealday_service.moose(current_user.id, file)

@mealday_router.post("/remove-moose") ##식단게시 취소시 임시파일삭제(임시저장사진명 필요:file_path)
@inject
async def remove_moose(
    file_path: Annotated[str, Form(..., description="moose로 얻은 file_path")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    moose 확인후 해당 사진 삭제
     - 입력예시 : file_path (moose api로 얻은 임시 파일경로)
     - 기능명세서 :
    """
    return mealday_service.remove_moose(file_path)

################################### Dish #########################################

dish_router = APIRouter(prefix="/api/v1/dish", tags=["dish"])

@dish_router.post("/r-v1/{daytime}/{routine_id}", response_model=APIResponse)
@inject
async def register_v1(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="기록일자 (형식: 2024-06-01)")],
    routine_id: Annotated[str, Path(..., description="트랙루틴id")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단등록 v1(체크 표시로 음식 일괄등록)
     - 입력예시 : daytime = 2024-06-01, routine_id = fdasfewaerwq
    """
    mealday_service.register_dish_v1(current_user.id, daytime, routine_id)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Post Success")

@dish_router.post("/r-v2/{daytime}/{routine_food_id}", response_model=APIResponse)
@inject
async def register_v2(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="기록일자 (형식: 2024-06-01)")],
    routine_food_id: Annotated[str, Path(..., description="루틴푸드id")],
    picture: Annotated[UploadFile, File(..., description="사진1개")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단등록 v2(계획된 트랙중 이미지가 없는 트랙의 이미지를 등록하기용
     - 입력예시 : daytime = 2024-06-01, routin_food_id = fdasfewaerwq, picture=사진파일1개
    """
    mealday_service.register_dish_v2(current_user.id, daytime, routine_food_id, picture)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Post Success")

@dish_router.post("/r-v3/{daytime}", response_model=APIResponse)
@inject
async def register_v3(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="기록일자 (형식: 2024-06-01)")],
    routine_food_ids: Annotated[List[str], Form(..., description="루틴푸드id")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단등록 v3(계획된 트랙중 특정 루틴푸드만 선택
     - 입력예시 : daytime = 2024-06-01, routin_food_ids = [fdasfewaerwq,dfas fdsa f], picture=사진파일1개
    """
    mealday_service.register_dish_v3(current_user.id, daytime, routine_food_ids)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Post Success")

@dish_router.post("/r-v4/{daytime}", response_model=APIResponse)
@inject
async def register_v4(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    daytime: Annotated[str, Path(description="기록일자 (형식: 2024-06-01)")],
    body: CreateDishBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    식단등록 v4(계획하지 않은 식단 등록
     - 입력예시 : daytime = 2024-06-01, body ={mealtime = 아침, days=3, name= "이름", label = 숫자 or None
    """
    mealday_service.register_dish_v4(current_user.id, daytime, body)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Post Success")

@dish_router.get("/{dish_id}", response_model=Dish_Full)
@inject
async def get_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    Dish 조회
     - 입력예시 : dish_id = dasfawerwreqw

    """
    return mealday_service.find_dish(current_user.id, dish_id)

@dish_router.get("/group/{track_id}", response_model=List[DishGroupResponse])
@inject
async def get_dish_not_routine(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    track_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    Dish 조회
     - 입력예시 : track_id = dasfawerwreqw

    """
    return mealday_service.get_dish_not_routine(current_user.id, track_id)

@dish_router.delete("/{dish_id}", response_model=APIResponse) ## 등록한 Dish 삭제
@inject
async def remove_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    Dish 삭제
    """
    mealday_service.remove_dish(current_user.id, dish_id)
    return APIResponse(status_code=status.HTTP_200_OK, message="Dish Delete Success")


@dish_router.patch("/{dish_id}", response_model=Dish_Full)
@inject
def update_dish(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    body: UpdateDishBody,
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    등록한 dish의 label 혹은 name 수량 변경,(변경되는 것만 입력바람 ex label +quantity, label, name + quantity/ name label 같이 ㄴㄴ
     - 입력예시 : dish_id = dsafeawewrqr,, body ={track_goal: true} / {
                                                                       {heart: true}/ {size: 200}
                                            {label: 1235}, {quantity: 5}  {size = 105.2}
    """

    return mealday_service.update_dish(current_user.id, dish_id, body)

@dish_router.patch("/image_url/{dish_id}", response_model=DishImageUrl)
@inject
def update_dish_image(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    dish_id: Annotated[str, Path(description=" (형식: dasfsdrewarq)")],
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service])
):
    """
    update dish 후 나온 dish_id를 활용하여 image_url을 변경한다
    """
    return mealday_service.update_dish_image(current_user.id, dish_id)
