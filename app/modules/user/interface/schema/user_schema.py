from datetime import datetime, date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, Field
from pydantic_core.core_schema import FieldValidationInfo

from app.core.auth import Role


class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'


class Rank(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    username: str = Field(min_length=2, max_length=32)
    nickname: str = Field(min_length=2, max_length=32)
    cellphone: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password1: str = Field(min_length=8, max_length=32)
    password2: str = Field(min_length=8, max_length=32)
    gender: Gender
    birth: date
    profile_picture: Optional[str] = Field(default=None, max_length=256)

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('Passwords do not match')
        return v


class UserResponse(BaseModel):
    username: str
    name: str
    email: str
    role: Role


class UserFcmToken(UserResponse):
    fcm_token: str


class UserInfoResponse(UserResponse):
    id: str
    username: str
    name: str
    email: str
    role: Role
    nickname: str
    cellphone: str
    gender: Gender
    birth: date
    rank: Rank
    profile_picture: str
    create_date: datetime
    update_date: datetime


class UpdateUserBody(BaseModel):
    nickname: Optional[str] = Field(default=None, min_length=2, max_length=32)
    password: Optional[str] = Field(default=None, min_length=8, max_length=32)
    password2: Optional[str] = Field(default=None, min_length=8, max_length=32)
    profile_picture: Optional[str] = Field(default=None, max_length=128)
    email: Optional[EmailStr] = Field(default=None, max_length=64)

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v
