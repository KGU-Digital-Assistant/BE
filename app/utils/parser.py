from http import HTTPStatus

from fastapi import HTTPException
from rich import status

from modules.track.interface.schema.track_schema import MealTime


def weekday_parse(weekday: str):
    weekday = weekday[0]
    if weekday == "월":
        return 1
    if weekday == "화":
        return 2
    if weekday == "수":
        return 3
    if weekday == "목":
        return 4
    if weekday == "금":
        return 5
    if weekday == "토":
        return 6
    if weekday == "일":
        return 7
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="Weekday not supported",
    )


def time_parse(_time: str):
    if _time == "아침":
        return MealTime.BREAKFAST
    if _time == "아점":
        return MealTime.BRUNCH
    if _time == "점심":
        return MealTime.LUNCH
    if _time == "점저":
        return MealTime.LINNER
    if _time == "저녁":
        return MealTime.DINNER
    if _time == "간식":
        return MealTime.SNACK
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="invalid time1"
    )