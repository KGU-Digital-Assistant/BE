from abc import ABC

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.testing import db

from database import SessionLocal, get_db
from modules.user.domain.repository.user_repo import IUserRepository
from modules.user.domain.user import User as UserVO
from modules.user.infra.db_models.user import User
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import CustomException


class UserRepository(IUserRepository, ABC):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: UserVO):
        new_user = User(
            id=user.id,
            name=user.name,
            email=user.email,
            username=user.username,
            nickname=user.nickname,
            cellphone=user.cellphone,
            gender=user.gender,
            rank=user.rank,
            profile_picture=user.profile_picture,
            password=user.password,
            birth=user.birth,
            fcm_token=user.fcm_token,
            role=user.role,
            create_date=user.create_date,
            update_date=user.update_date,
        )
        self.db.add(new_user)
        self.db.commit()

        return new_user

    def find_by_email(self, email: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()

        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        return UserVO(**row_to_dict(user))

    def find_by_id(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()

        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        return UserVO(**row_to_dict(user))

    def find_by_cellphone(self, cellphone: str):
        user = self.db.query(User).filter(User.cellphone == cellphone).first()
        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)
        return UserVO(**row_to_dict(user))

    def find_by_nickname(self, nickname: str):
        user = self.db.query(User).filter(User.nickname == nickname).first()
        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)
        return UserVO(**row_to_dict(user))

    def find_by_username(self, username: str):
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)
        return UserVO(**row_to_dict(user))

    def update(self, user_vo: UserVO):
        user = self.db.query(User).filter(User.id == user_vo.id).first()
        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        user.email = user_vo.email
        user.nickname = user_vo.nickname
        user.password = user_vo.password
        user.profile_picture = user_vo.profile_picture
        user.update_date = user_vo.update_date

        self.db.commit()
        return UserVO(**row_to_dict(user))

    # def get_users(
    #         self,
    #         page: int = 1,
    #         items_per_page: int = 10,
    # ) -> tuple[int, list[UserVO]]:
    #     with SessionLocal() as db:
    #         query = db.query(User)
    #         total_count = query.count()
    #
    #         offset = (page - 1) * items_per_page
    #         users = query.limit(items_per_page).offset(offset).all()

        # return total_count, [UserVO(**row_to_dict(user)) for user in users]

    def delete(self, id: str):
        user = self.db.query(User).filter(User.id == id).first()

        if not user:
            raise CustomException(ErrorCode.USER_NOT_FOUND)

        self.db.delete(user)
        self.db.commit()
