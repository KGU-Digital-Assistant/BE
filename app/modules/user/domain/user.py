from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pydantic import EmailStr

from core.auth import Role
from modules.user.interface.schema.user_schema import Gender, Rank


@dataclass
class User:
    id: str
    name: str
    username: str
    nickname: str
    cellphone: str
    email: EmailStr
    password: str
    gender: Gender
    birthday: datetime.date
    rank: Rank
    role: Role
    profile_picture: str | None
    fcm_token: str | None
    # mentor_id: str | None
    created_date: datetime
    updated_date: datetime