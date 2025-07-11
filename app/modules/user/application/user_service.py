from datetime import datetime
from dependency_injector.wiring import inject
from app.core.auth import create_access_token, Role
from app.core.fcm import encrypt_token
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.user.domain.user import User
from app.modules.user.interface.schema.user_schema import CreateUserBody, Rank, UpdateUserBody, UserResponse, \
    UserInfoResponse
from app.utils.crypto import Crypto
from app.utils.db_utils import orm_to_pydantic, dataclass_to_pydantic
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error


class UserService:
    @inject
    def __init__(
            self,
            user_repo: IUserRepository,
            crypto: Crypto,
    ):
        self.user_repo = user_repo
        self.crypto = crypto

    def create_user(
            self,
            # background_tasks: BackgroundTasks,
            user: CreateUserBody
    ):
        if self.user_repo.find_by_email(user.email): raise raise_error(ErrorCode.USER_ALREADY_EXIST_EMAIL)
        if self.user_repo.find_by_nickname(user.nickname): raise raise_error(ErrorCode.USER_ALREADY_EXIST_NICKNAME)
        if self.user_repo.find_by_cellphone(user.cellphone): raise raise_error(ErrorCode.USER_ALREADY_EXIST_CELLPHONE)
        if self.user_repo.find_by_username(user.username): raise raise_error(ErrorCode.USER_ALREADY_EXIST_USERNAME)
        user.password1 = self.crypto.encrypt(user.password1)
        return self.user_repo.save(user)

    def login(self, username: str, password: str):
        user = self.user_repo.find_by_username(username)
        if not user:
            raise raise_error(ErrorCode.USER_NOT_FOUND)
        if not (self.crypto.verify(password, user.password)):
            raise raise_error(ErrorCode.PASSWORD_INVALID)

        return create_access_token(
            payload={"user_id": user.id},
            role=user.role
        )

    def delete_user(self, id: str):
        self.user_repo.delete(id)

    def validate_user_update(self, body: UpdateUserBody, cur_user: User):
        """유효성 검사: 닉네임 & 이메일 중복 체크"""
        if not cur_user:
            raise raise_error(ErrorCode.USER_NOT_FOUND)
        nick_user = self.user_repo.find_by_nickname(body.nickname)
        email_user = self.user_repo.find_by_email(body.email)
        if body.nickname and nick_user is not None and nick_user.id != cur_user.id:
            raise raise_error(ErrorCode.USER_ALREADY_EXIST_NICKNAME)
        if body.email and email_user is not None and email_user.id != cur_user.id:
            raise raise_error(ErrorCode.USER_ALREADY_EXIST_EMAIL)

    def apply_updates(self, user, body: UpdateUserBody):
        """사용자 정보 업데이트 적용"""
        if body.nickname: user.nickname = body.nickname
        if body.password: user.password = self.crypto.encrypt(body.password)
        if body.profile_picture: user.profile_picture = body.profile_picture
        if body.email: user.email = body.email

        user.update_date = datetime.now()

    def update_user(self, id: str, body: UpdateUserBody):
        user = self.user_repo.find_by_id(id)

        self.validate_user_update(body, user)  # ✅ 별도 검증 함수로 분리
        self.apply_updates(user, body)
        return self.user_repo.update(user)

    def get_user_info(self, id: str):
        user = self.user_repo.find_by_id(id)
        if not user:
            raise raise_error(ErrorCode.USER_NOT_FOUND)
        return user

    def save_fcm_token(self, id: str, token: str):
        user = self.user_repo.find_by_id(id)
        if not user:
            raise raise_error(ErrorCode.USER_NOT_FOUND)
        user.fcm_token = encrypt_token(token)
        return self.user_repo.save_fcm_token(user)

    def get_users_by_username(self, username: str):
        user_list = self.user_repo.find_by_username_all(username)
        return user_list

    def get_user_by_id(self, user_id: str):
        return self.user_repo.find_by_id(user_id)
