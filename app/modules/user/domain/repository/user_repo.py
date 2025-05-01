from abc import ABCMeta, abstractmethod

from sqlalchemy.orm import Session

from app.modules.user.domain.user import User
from app.modules.user.interface.schema.user_schema import CreateUserBody


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: CreateUserBody):
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def update(self, user_vo: User):
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id):
        raise NotImplementedError

    @abstractmethod
    def find_by_nickname(self, nickname: str):
        raise NotImplementedError

    @abstractmethod
    def find_by_cellphone(self, cellphone: str):
        raise NotImplementedError

    @abstractmethod
    def find_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    def save_fcm_token(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def find_by_username_all(self, username: str):
        raise NotImplementedError

    # @abstractmethod
    # def find_users_mentor_info_by_user_id(self, user_id: str):
    #     raise NotImplementedError