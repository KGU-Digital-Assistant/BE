from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum
from typing import Annotated

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app_config import Settings, get_settings
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error

settings = get_settings()

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"


class Role(Enum):
    USER = "USER"
    TRAINER = "TRAINER"
    ADMIN = "ADMIN"


def create_access_token(
        payload: dict,
        role: Role,
        expires_delta: timedelta = timedelta(hours=6),
):
    expire = datetime.utcnow() + expires_delta
    payload.update(
        {
            "role": role.value,
            "exp": expire,
        }
    )
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


@dataclass
class CurrentUser:
    id: str
    role: Role

    def __str__(self):
        return f"{self.id}({self.role})"


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id or not role or role != Role.USER.value:
        raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)

    return CurrentUser(user_id, Role(role))


def get_admin_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)

    role = payload.get("role")
    if not role or role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return CurrentUser("ADMIN_USER_ID", role)
