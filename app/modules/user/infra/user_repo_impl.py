from abc import ABC
from datetime import datetime

from ulid import ULID

from app.core.auth import Role
from app.database import SessionLocal
from app.modules.user.domain.repository.user_repo import IUserRepository
from app.modules.user.domain.user import User as UserVO
from app.modules.user.infra.db_models.user import User#, Mentor
from app.modules.user.interface.schema.user_schema import CreateUserBody, Rank
from app.utils.db_utils import row_to_dict
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error


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
            return db.query(User).filter(User.email == email).first()

    def find_by_id(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()
            if not user:
                return None
            return UserVO(**row_to_dict(user))

    def find_by_cellphone(self, cellphone: str):
        with SessionLocal() as db:
            return db.query(User).filter(User.cellphone == cellphone).first()

    def find_by_nickname(self, nickname: str):
        with SessionLocal() as db:
            return db.query(User).filter(User.nickname == nickname).first()

    def find_by_username(self, username: str):
        with SessionLocal() as db:
            return db.query(User).filter(User.username == username).first()

    def update(self, _user: User):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == _user.id).first()
            user.email = _user.email
            user.nickname = _user.nickname
            user.password = _user.password
            user.profile_picture = _user.profile_picture
            user.update_date = _user.update_date

            db.commit()
            return UserVO(**row_to_dict(user))

    def delete(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()
            if not user:
                raise raise_error(ErrorCode.USER_NOT_FOUND)

            db.delete(user)
            db.commit()

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
            user_vo_list = []
            for user in user_list:
                user_vo_list.append(UserVO(**row_to_dict(user)))
            return user_vo_list

    # def find_users_mentor_info_by_user_id(self, user_id: str):### 유저의 멘토id를 활용해서 멘토의 user_id를 찾기
    #     with SessionLocal() as db:
    #         user= db.query(User).filter(User.id==user_id).first()
    #         if user and user.mentor_id:
    #             mentor = db.query(Mentor).filter(Mentor.id==user.mentor_id).first()
    #             return {"mentor_user_id": mentor.user_id, "username": user.name}
    #         return None