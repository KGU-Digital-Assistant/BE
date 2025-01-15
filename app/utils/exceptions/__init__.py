from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .handlers import (
    CustomException,
    custom_exception_handler
)

