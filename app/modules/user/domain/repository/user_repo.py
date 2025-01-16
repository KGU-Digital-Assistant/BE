from abc import ABCMeta, abstractmethod

from sqlalchemy.orm import Session

from modules.user.domain.user import User as User


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email):
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
