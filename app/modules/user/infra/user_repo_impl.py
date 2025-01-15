from abc import ABC

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.testing import db

from database import SessionLocal, get_db
from modules.user.domain.repository.user_repo import IUserRepository
from modules.user.domain.user import User as UserVO
from modules.user.infra.db_models.user import User
from utils.db_utils import row_to_dict


class UserRepository(IUserRepository, ABC):
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def save(self, user: UserVO, db: Session):
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
            birth=user.birthday,
            fcm_token=user.fcm_token,
            role=user.role,
            create_date=user.created_date,
            update_date=user.updated_date,
        )
        try:
            self.db.add(new_user)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=403,

            )

        return new_user

    def find_by_email(self, email: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=422)

        return UserVO(**row_to_dict(user))

    def find_by_id(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()

        if not user:
            raise HTTPException(status_code=422)

        return UserVO(**row_to_dict(user))

    def update(self, user_vo: UserVO):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_vo.id).first()

            if not user:
                raise HTTPException(status_code=422)

            user.name = user_vo.name
            user.password = user_vo.password

            db.add(user)
            db.commit()

        return user

    def get_users(
            self,
            page: int = 1,
            items_per_page: int = 10,
    ) -> tuple[int, list[UserVO]]:
        with SessionLocal() as db:
            query = db.query(User)
            total_count = query.count()

            offset = (page - 1) * items_per_page
            users = query.limit(items_per_page).offset(offset).all()

        return total_count, [UserVO(**row_to_dict(user)) for user in users]

    def delete(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()

            if not user:
                raise HTTPException(status_code=422)

            db.delete(user)
            db.commit()

