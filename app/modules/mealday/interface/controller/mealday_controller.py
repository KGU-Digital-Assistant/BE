from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, Query

from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from containers import Container
from core.auth import CurrentUser, get_current_user
from database import get_db
from modules.mealday.application.mealday_service import MealDayService
from modules.mealday.domain.mealday import MealDay
from modules.mealday.interface.schema.mealday_schema import CreateMealDayBody,MealDayResponse_date
from utils.responses.response import create_response

router = APIRouter(prefix="/mealday")


def dataclass_to_pydantic(mealday: MealDay) -> MealDayResponse_date:
    return MealDayResponse_date(**{key: value for key, value in mealday.__dict__.items() if key in MealDayResponse_date.__annotations__})

@router.post("/create")
@inject
def create_mealday(
        mealday: CreateMealDayBody,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        mealday_service: MealDayService = Depends(Provide[Container.mealday_service]),
        db: Session = Depends(get_db),
):
    new_mealday = mealday_service.create_mealday(mealday, current_user.id)
    return create_response(dataclass_to_pydantic(new_mealday))

@router.get("/get_mealday")
@inject
def get_mealday_by_date(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    record_date: date = Query(..., description="조회할 날짜"),
    mealday_service: MealDayService = Depends(Provide[Container.mealday_service]),
    db: Session = Depends(get_db),
):
    mealday = mealday_service.find_mealday_by_date(record_date, current_user.id)
    return create_response(dataclass_to_pydantic(mealday))
