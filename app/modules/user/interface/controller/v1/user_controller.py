from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends

from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from containers import Container
from core.auth import CurrentUser, get_current_user
from modules.user.application.user_service import UserService
from modules.user.interface.schema.user_schema import CreateUserBody, UserResponse, UpdateUserBody, UserInfoResponse, \
    UserFcmToken
from utils.phone_verify import PhoneNumberRequest, VerificationRequest, send_code, verify_code
from utils.responses.response import APIResponse


router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/create", response_model=UserResponse)
@inject
def create_user(
        user: CreateUserBody,
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    return user_service.create_user(user)


@router.delete("/delete", response_model=APIResponse)
@inject
def delete_user(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    user_service.delete_user(current_user.id)
    return APIResponse(status_code=status.HTTP_200_OK, message="User deleted")


@router.put("/update", response_model=UserInfoResponse)
@inject
def update_user(
        body: UpdateUserBody,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    ### 유저 업데이트
    - 변경사항 없는 값은 json 넘길때 아예 제외하면 됨.
    """
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


@router.get("/info", response_model=UserInfoResponse)
@inject
def get_user_info(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    현재 유저 정보 불러오기
    """
    return user_service.get_user_info(current_user.id)


@router.post("/fcm-token", response_model=UserFcmToken)
@inject
def save_fcm_token(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        token: str,
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    클라이언트(프론트)에서 FCM 토큰을 발급받아서 서버에 저장하는 API
    - 회원가입 후 바로 할 것 권장
    """
    return user_service.save_fcm_token(current_user.id, token)


@router.get("/username", response_model=List[UserInfoResponse])
@inject
def get_users_by_username(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        username: str,
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    검색 기능: 검색단어에 포함된 username를 가진 유저 리스트 반환, LIKE "%username%"
    """
    return user_service.get_users_by_username(username)


@router.post("/send-code/", response_model=APIResponse)
def phone_send_code(
        request: PhoneNumberRequest,
):
    """
    휴대폰 인증번호 보내기
    """
    send_code(request.phone_number)
    return APIResponse(status_code=status.HTTP_200_OK)


@router.post("/verify-code/", response_model=APIResponse)
def phone_verify_code(
        request: VerificationRequest,
):
    """
    휴대폰 인증번호 검증하기
    """
    message = verify_code(request.phone_number, request.code)
    return APIResponse(status_code=status.HTTP_200_OK, data=message)
