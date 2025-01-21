from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from containers import Container
from core.auth import CurrentUser, get_current_user
from database import get_db
from modules.user.application.user_service import UserService
from modules.user.domain.user import User
from modules.user.interface.schema.user_schema import CreateUserBody, UserResponse, UpdateUserBody
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import CustomException
from utils.responses.response import create_response
from utils.responses.response_schema import APIResponse

router = APIRouter(prefix="/users")


def dataclass_to_pydantic(user: User) -> UserResponse:
    return UserResponse(**{key: value for key, value in user.__dict__.items() if key in UserResponse.__annotations__})


@router.post("/create")
@inject
def create_user(
        user: CreateUserBody,
        user_service: UserService = Depends(Provide[Container.user_service]),
        db: Session = Depends(get_db),
):
    new_user = user_service.create_user(user)
    return create_response(dataclass_to_pydantic(new_user))


@router.delete("/delete")
@inject
def delete_user(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    user_service.delete_user(current_user.id)


@router.put("/update")
@inject
def update_user(
        body: UpdateUserBody,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    return user_service.update_user(current_user.id, body)


@router.post("/login")
@inject
def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    access_token = user_service.login(
        username=form_data.username,
        password=form_data.password,
    )

    return {"access_token": access_token, "token_type": "bearer"}
