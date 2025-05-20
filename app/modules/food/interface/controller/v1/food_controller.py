from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide
from app.containers import Container
from typing import List
from app.modules.food.application.food_service import FoodService
from app.modules.food.interface.schema.food_schema import FoodData


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
