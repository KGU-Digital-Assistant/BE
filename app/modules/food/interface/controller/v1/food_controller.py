from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide
from containers import Container
from core.auth import CurrentUser, get_current_user
from modules.food.application.food_service import FoodService
from modules.food.interface.schema.food_schema import Food_Data


router = APIRouter(prefix="/api/v1/food", tags=["food"])

@router.get("/get/food_data", response_model=Food_Data)
@inject
def get_food_data(
    name: str = Query(..., description="조회할 음식명"),
    food_service: FoodService = Depends(Provide[Container.food_service])
):
    """
    음식명 입력후 칼로리 조회
    """
    return food_service.get_food_data(name)
