from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

from starlette.config import Config

# # .env 파일 강제 로드
# load_dotenv(dotenv_path=".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    JWT_SECRET_KEY: str
    SQLALCHEMY_DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str
    REDIRECT_URI: str
    FIREBASE_FCM_API_KEY: str
    FIREBASE_PATH: str
    FIREBASE_BUCKET: str
    SID: str
    AUTH_TOKEN: str
    PHONE_NUMBER: str
    SMS_KEY: str
    SMS_SECRET_KEY: str
    MY_PHONE_NUMBER: str
    FERNET_KEY: str

@lru_cache
def get_settings():
    return Settings()


# 디버깅 코드
# if __name__ == "__main__":
#     settings = Settings()
#     print("POSTGRES_USER:", os.getenv("POSTGRES_USER"))
#     print("SQLALCHEMY_DATABASE_URL:", os.getenv("SQLALCHEMY_DATABASE_URL"))
#     print("Pydantic Settings:", settings.dict())
