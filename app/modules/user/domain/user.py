from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pydantic import EmailStr

from app.core.auth import Role
from app.modules.user.interface.schema.user_schema import Gender, Rank


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
    birth: datetime.date
    rank: Rank
    role: Role
    profile_picture: str | None
    fcm_token: str | None
    # mentor_id: str | None
    create_date: datetime
    update_date: datetime

# @dataclass
# class Mentor:
#     id: str
#     user_id: str
#     gym: str | None
#     FA: bool | None