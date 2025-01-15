from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from containers import Container
from modules.user.application.user_service import UserService
from modules.user.interface.schema.user_schema import CreateUserBody, UserResponse

router = APIRouter(prefix="/users")


@router.post("/create", response_model=UserResponse)
@inject
def create_user(
        user: CreateUserBody,
        user_service: UserService = Depends(Provide[Container.user_service])):
    new_user = user_service.create_user(user)
    return new_user


@router.post("/login")
@inject
def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    access_token = user_service.login(
        email=form_data.username,
        password=form_data.password,
    )

    return {"access_token": access_token, "token_type": "bearer"}
