# app/utils/api_response.py

from pydantic import BaseModel
from typing import Any, Optional


class APIResponse(BaseModel):
    status_code: int  # ✅ HTTP 상태 코드
    message: str = "success" # ✅ 응답 메시지
    data: Optional[Any] = None  # ✅ 성공 시 데이터
