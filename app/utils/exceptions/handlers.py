from fastapi import HTTPException

from app.utils.exceptions.error_code import ErrorCode
from app.utils.responses.response import APIResponse


def raise_error(error_code: ErrorCode):
    """❌ 공통 에러 처리 함수"""
    raise HTTPException(
        status_code=error_code.code,
        detail=APIResponse(status_code=error_code.code, message=error_code.message).dict()
    )

