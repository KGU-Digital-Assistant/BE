from datetime import datetime, date
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from core.auth import Role


class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'


class Rank(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


class CreateUserBody(BaseModel):
    name: str
    username: str
    nickname: str
    cellphone: str
    email: EmailStr
    password1: str
    password2: str
    gender: Gender
    rank: Rank
    birth: date
    role: Role
    profile_picture: str

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('Passwords do not match')
        return v


class UserResponse(BaseModel):
    name: str
    email: str
