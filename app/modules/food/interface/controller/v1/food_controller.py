from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide
from starlette import status

from app.containers import Container
from typing import List, Annotated

from app.core.auth import CurrentUser, get_current_user, get_admin_user
from app.modules.food.application.food_service import FoodService
from app.modules.food.interface.schema.food_schema import FoodData
from app.utils.responses.response import APIResponse

router = APIRouter(prefix="/api/v1/foods", tags=["Food"])


@router.get("/search", response_model=List[FoodData])
@inject
def search_food_data(
    name: str = Query(..., description="조회할 음식명"),
    food_service: FoodService = Depends(Provide[Container.food_service])
):
    """
    음식명 입력후 칼로리 조회
    """
    return food_service.search_food_data(name)


@router.get("/{food_label}", response_model=FoodData)
@inject
def get_food_data(
    food_label: int,
    food_service: FoodService = Depends(Provide[Container.food_service])
):
    """
    food label로 GET
    """
    return food_service.get_food_data(food_label)


@router.post("/", response_model=APIResponse)
@inject
def post_food_data(
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    food_service: FoodService = Depends(Provide[Container.food_service])
):
    food_service.insert_food_data()
    return APIResponse(status_code=status.HTTP_201_CREATED, message="데이터 삽입 성공")
