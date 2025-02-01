from enum import Enum
from fastapi import HTTPException, status


class ErrorCode(Enum):

    UNPROCESSABLE_ENTITY = (status.HTTP_422_UNPROCESSABLE_ENTITY, "올바른 요청이지만 요청된 지시에 따를 수 없습니다.")

    # User 관련 에러 코드
    PASSWORD_INVALID = (status.HTTP_401_UNAUTHORIZED, "비밀번호가 틀립니다.")
    USER_NOT_AUTHENTICATED = (status.HTTP_401_UNAUTHORIZED, "로그인에 실패했습니다.")
    USER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "사용자 정보가 존재하지 않습니다.")
    USER_ALREADY_EXIST = (status.HTTP_409_CONFLICT, "이미 존재하는 회원입니다.")
    USER_ALREADY_EXIST_CELLPHONE = (status.HTTP_409_CONFLICT, "중복된 휴대폰 번호입니다.")
    USER_ALREADY_EXIST_EMAIL = (status.HTTP_409_CONFLICT, "중복된 이메일 입니다")
    USER_ALREADY_EXIST_NICKNAME = (status.HTTP_409_CONFLICT, " 중복된 닉네임 입니다.")

    # MealDay 관련 에러 코드
    MEALDAY_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "식단(일일)가 존재하지 않습니다.")

    # db 관련 에러 코드
    DATABASE_SAVE_FAIL = (status.HTTP_500_INTERNAL_SERVER_ERROR, "데이터베이스 저장에 실패했습니다.")

    MEMBER_NOT_AUTHENTICATED = (status.HTTP_401_UNAUTHORIZED, "로그인하지 않은 사용자입니다")
    MEMBER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "사용자 정보가 존재하지 않습니다")
    DUPLICATE_MEMBER_LOGIN_ID = (status.HTTP_409_CONFLICT, "중복된 로그인 아이디입니다")
    DUPLICATE_MEMBER_PHONE_NUMBER = (status.HTTP_409_CONFLICT, "중복된 전화번호입니다")
    DUPLICATE_MEMBER_NICKNAME = (status.HTTP_400_BAD_REQUEST, "중복된 닉네임입니다")
    PROFILE_IMAGE_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "프로필 이미지를 찾을 수 없습니다")
    MEMBER_NOT_ADMIN = (status.HTTP_403_FORBIDDEN, "관리자가 아닙니다")
    MYINFO_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "내 정보를 찾을 수 없습니다")

    @property
    def status_code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]
