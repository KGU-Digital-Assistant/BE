from abc import ABC
from datetime import datetime

from ulid import ULID

from core.auth import Role
from database import SessionLocal
from modules.user.domain.repository.user_repo import IUserRepository
from modules.user.domain.user import User as UserVO
from modules.user.infra.db_models.user import User
from modules.user.interface.schema.user_schema import CreateUserBody, Rank
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error


class UserRepository(IUserRepository, ABC):
    def save(self, user: CreateUserBody):
        now = datetime.now()
        with SessionLocal() as db:
            new_user = User(
                id=str(ULID()),
                name=user.name,
                email=user.email,
                username=user.username,
                nickname=user.nickname,
                cellphone=user.cellphone,
                gender=user.gender,
                rank=Rank.BRONZE,
                profile_picture=user.profile_picture,
                password=user.password1,
                birth=user.birth,
                fcm_token="",
                role=Role.USER,
                create_date=now,
                update_date=now,
            )
            db.add(new_user)
            db.commit()

            return UserVO(**row_to_dict(new_user))

    def find_by_email(self, email: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()

        return user

    def find_by_id(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()

        return user
        # return UserVO(**row_to_dict(user))

    def find_by_cellphone(self, cellphone: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.cellphone == cellphone).first()

        return user

    def find_by_nickname(self, nickname: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.nickname == nickname).first()

        return user

    def find_by_username(self, username: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == username).first()

        return user

    def update(self, user: User):
        with SessionLocal() as db:

            user.email = user.email
            user.nickname = user.nickname
            user.password = user.password
            user.profile_picture = user.profile_picture
            user.update_date = user.update_date

            db.commit()
        return user

    def delete(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()
            if not user:
                raise raise_error(ErrorCode.USER_NOT_FOUND)

            db.delete(user)
            db.commit()
        return True

    def save_fcm_token(self, user_vo: User):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_vo.id).first()
            if not user:
                raise raise_error(ErrorCode.USER_NOT_FOUND)

            user.fcm_token = user_vo.fcm_token
            db.commit()
        return UserVO(**row_to_dict(user))

    def find_by_username_all(self, username: str):
        with SessionLocal() as db:
            user_list = db.query(User).filter(User.username == username).all()

        # res = [UserVO(**row_to_dict(user)) for user in user_list]
        return user_list
