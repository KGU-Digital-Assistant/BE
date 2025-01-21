from fastapi import HTTPException

from utils.exceptions.error_code import ErrorCode
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class CustomException(HTTPException):
    def __init__(self, error: ErrorCode):
        super().__init__(
            status_code=error.status_code,
            detail={"error_code": error.name, "message": error.message}
        )


async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )
