from http.client import HTTPException

from pydantic import BaseModel, field_validator
import random
import requests
import time
import datetime
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from starlette.config import Config
from pydantic import BaseModel
from app.app_config import get_settings
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error

setting = get_settings()

# CoolSMS 설정
api_key = setting.SMS_KEY
api_secret = setting.SMS_SECRET_KEY
from_number = setting.MY_PHONE_NUMBER
url = "https://api.coolsms.co.kr/messages/v4/send"

# 메모리 내에 인증 코드를 저장할 딕셔너리
verification_codes = {}


class PhoneNumberRequest(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    def remove_hyphens(cls, value: str) -> str:
        """
        입력된 휴대폰 번호에서 하이픈(-)을 제거.
        """
        return value.replace("-", "")


class VerificationRequest(PhoneNumberRequest):
    code: str


def send_code(phone_number: str):
    try:
        res = send_verification_code(phone_number)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    if res is None:
        raise raise_error(ErrorCode.CODE_SEND_FAIL)


def verify_code(phone_number: str, code: str):
    try:
        success, message = check_verification_code(phone_number, code)
        if success:
            return message
        else:
            raise raise_error(ErrorCode.CODE_VERIFY_FAIL)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = timedelta(seconds=-utc_offset_sec)
    return datetime.now().replace(tzinfo=timezone(offset=utc_offset)).isoformat()


def get_signature(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(apiKey, apiSecret):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {'Authorization': 'HMAC-SHA256 ApiKey=' + apiKey + ', Date=' + date + ', salt=' + salt + ', signature=' +
                             get_signature(apiSecret, data)}


def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_code(phone_number: str):
    code = generate_verification_code()
    expiration_time = datetime.now() + timedelta(minutes=3)
    verification_codes[phone_number] = (code, expiration_time)

    headers = get_headers(api_key, api_secret)
    data = {
        "message": {
            "to": phone_number,
            "from": from_number,
            "text": f"[I-EAT] 인증번호: {code}"
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to send SMS: {response.text}")

    return code


def check_verification_code(phone_number: str, code: str):
    if phone_number in verification_codes:
        stored_code, expiration_time = verification_codes[phone_number]
        if datetime.now() > expiration_time:
            del verification_codes[phone_number]
            return False, "Verification code expired"
        if stored_code == code:
            del verification_codes[phone_number]
            return True, "Phone number verified"
    return False, "Invalid verification code"