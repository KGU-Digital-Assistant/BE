from enum import Enum
from fastapi import HTTPException, status


class ErrorCode(Enum):
    # Track 관련 에러 코드
    ROUTINE_DAYS_SO_OVER = (status.HTTP_400_BAD_REQUEST, "루틴 days가 트랙 duration보다 큽니다.")
    TRACK_ROUTINE_DATE_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "루틴 Date가 존재하지 않습니다.")
    TRACK_ROUTINE_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "루틴이 존재하지 않습니다.")
    TRACK_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "트랙이 존재하지 않습니다.")

    # Participant 관련 에러 코드
    PARTICIPANT_ALREADY_EXIST = (status.HTTP_409_CONFLICT, "이미 트랙에 참여중입니다.")

    # 인증
    CODE_VERIFY_FAIL = (status.HTTP_400_BAD_REQUEST, "인증 코드가 올바르지 않습니다.")
    CODE_SEND_FAIL = (status.HTTP_502_BAD_GATEWAY, "휴대폰 인증 코드 발송에 실패했습니다.")
    UNPROCESSABLE_ENTITY = (status.HTTP_422_UNPROCESSABLE_ENTITY, "올바른 요청이지만 요청된 지시에 따를 수 없습니다.")

    # User 관련 에러 코드
    PASSWORD_INVALID = (status.HTTP_401_UNAUTHORIZED, "비밀번호가 틀립니다.")
    USER_NOT_AUTHENTICATED = (status.HTTP_401_UNAUTHORIZED, "로그인에 실패했습니다.")
    USER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "사용자 정보가 존재하지 않습니다.")
    USER_ALREADY_EXIST = (status.HTTP_409_CONFLICT, "이미 존재하는 회원입니다.")
    USER_ALREADY_EXIST_CELLPHONE = (status.HTTP_409_CONFLICT, "중복된 휴대폰 번호입니다.")
    USER_ALREADY_EXIST_EMAIL = (status.HTTP_409_CONFLICT, "중복된 이메일 입니다")
    USER_ALREADY_EXIST_NICKNAME = (status.HTTP_409_CONFLICT, " 중복된 닉네임 입니다.")
    USER_ALREADY_EXIST_USERNAME = (status.HTTP_409_CONFLICT, "중복된 username입니다.")

    # MealDay 관련 에러 코드
    MEALDAY_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "식단(일일)가 존재하지 않습니다.")

    # db 관련 에러 코드
    DATABASE_SAVE_FAIL = (status.HTTP_500_INTERNAL_SERVER_ERROR, "데이터베이스 저장에 실패했습니다.")

    # 기타
    MEMBER_NOT_AUTHENTICATED = (status.HTTP_401_UNAUTHORIZED, "로그인하지 않은 사용자입니다")
    MEMBER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "사용자 정보가 존재하지 않습니다")
    DUPLICATE_MEMBER_LOGIN_ID = (status.HTTP_409_CONFLICT, "중복된 로그인 아이디입니다")
    DUPLICATE_MEMBER_PHONE_NUMBER = (status.HTTP_409_CONFLICT, "중복된 전화번호입니다")
    DUPLICATE_MEMBER_NICKNAME = (status.HTTP_400_BAD_REQUEST, "중복된 닉네임입니다")
    PROFILE_IMAGE_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "프로필 이미지를 찾을 수 없습니다")
    MEMBER_NOT_ADMIN = (status.HTTP_403_FORBIDDEN, "관리자가 아닙니다")
    MYINFO_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "내 정보를 찾을 수 없습니다")

    def __init__(self, code, message):
        self.code = code
        self.message = message
