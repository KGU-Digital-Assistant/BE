from datetime import datetime

import ulid
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from ulid import ULID
from dependency_injector.wiring import inject, Container, Provide

from core.auth import create_access_token, Role
from database import get_db
from modules.user.domain.repository import user_repo
from modules.user.domain.repository.user_repo import IUserRepository
from modules.user.domain.user import User
from modules.user.interface.schema.user_schema import CreateUserBody, Rank, UpdateUserBody
from utils.crypto import Crypto
from utils.db_utils import is_similar
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import CustomException


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
        _user_email = None
        _user_nickname = None
        _user_cellphone = None
        try:
            _user_email = self.user_repo.find_by_email(user.email)
        except HTTPException as e:
            if e.status_code != 404:
                raise HTTPException(status_code=e.status_code, detail=e.detail)
        try:
            _user_nickname = self.user_repo.find_by_nickname(user.nickname)
        except HTTPException as e:
            if e.status_code != 404:
                raise HTTPException(status_code=e.status_code, detail=e.detail)
        try:
            _user_cellphone = self.user_repo.find_by_cellphone(user.cellphone)
        except HTTPException as e:
            if e.status_code != 404:
                raise HTTPException(status_code=e.status_code, detail=e.detail)

        if _user_email:
            raise CustomException(ErrorCode.USER_ALREADY_EXIST_EMAIL)
        if _user_nickname:
            raise CustomException(ErrorCode.USER_ALREADY_EXIST_NICKNAME)
        if _user_cellphone:
            raise CustomException(ErrorCode.USER_ALREADY_EXIST_CELLPHONE)

        now = datetime.now()
        new_id = ULID()
        new_user: User = User(
            id=str(new_id),
            username=user.username,
            nickname=user.nickname,
            cellphone=user.cellphone,
            name=user.name,
            email=user.email,
            gender=user.gender,
            rank=Rank.BRONZE,
            birth=user.birth,
            password=self.crypto.encrypt(user.password1),
            create_date=now,
            update_date=now,
            fcm_token="default",
            profile_picture=user.profile_picture,
            role=Role.USER
        )
        self.user_repo.save(new_user)

        return new_user

    def login(self, username: str, password: str):
        user = self.user_repo.find_by_username(username)

        if not (self.crypto.verify(password, user.password)):
            raise CustomException(ErrorCode.PASSWORD_INVALID)

        access_token = create_access_token(
            payload={"user_id": user.id},
            role=Role.USER,
        )

        return access_token

    def delete_user(self, id: str):
        self.user_repo.delete(id)

    def update_user(self, id: str, body: UpdateUserBody):
        user = self.user_repo.find_by_id(id)
        _user_email = None
        _user_nickname = None
        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        _user_email = (
            self.user_repo.find_by_nickname(body.nickname)
            if not (_exc := HTTPException(status_code=404))
            else None
        )
        if _user_email:
            raise CustomException(ErrorCode.USER_ALREADY_EXIST_EMAIL)

        _user_nickname = (
            self.user_repo.find_by_cellphone(body.cellphone)
            if not (_exc := HTTPException(status_code=404))
            else None
        )
        if _user_nickname:
            raise CustomException(ErrorCode.USER_ALREADY_EXIST_NICKNAME)

        if body.nickname:
            user.nickname = body.nickname
        if body.password:
            user.password = self.crypto.encrypt(body.password)
        if body.profile_picture:
            user.profile_picture = body.profile_picture
        if body.email:
            user.email = body.email
        user.update_date = datetime.now()

        return self.user_repo.update(user)

    def get_user_info(self, id: str):
        return self.user_repo.find_by_id(id)

    def save_fcm_token(self, id: str, token: str):
        user = self.user_repo.find_by_id(id)
        user.fcm_token = token

        try:
            userVO = self.user_repo.save_fcm_token(user)
            return userVO
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    def get_users_by_username(self, username: str, id: str):
        user = self.user_repo.find_by_id(id)
        if user is None:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        user_list = self.user_repo.find_by_username_all(username)
        res = []
        for user in user_list:
            if is_similar(user.username, username):
                res.append(user)
        return res
