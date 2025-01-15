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
from modules.user.interface.schema.user_schema import CreateUserBody
from utils.crypto import Crypto


class UserService:
    @inject
    def __init__(
            self,
            user_repo: IUserRepository,
            crypto: Crypto,
            # ulid: ULID
            db: Session = Depends(get_db),
    ):
        self.user_repo = user_repo
        self.crypto = crypto
        # self.ulid = ulid
        self.db = db

    def create_user(
            self,
            # background_tasks: BackgroundTasks,
            user: CreateUserBody
    ):
        _user = None
        try:
            _user = self.user_repo.find_by_email(user.email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(status_code=422)

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
            rank=user.rank,
            birthday=user.birth,
            password=self.crypto.encrypt(user.password1),
            created_date=now,
            updated_date=now,
            fcm_token="default",
            profile_picture=user.profile_picture,
            role=user.role
        )
        self.user_repo.save(new_user, self.db)

        return new_user

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email)

        if not (self.crypto.verify(password, user.password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(
            payload={"user_id": user.id},
            role=Role.USER,
        )

        return access_token
