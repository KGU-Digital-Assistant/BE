from typing import Any, List, Optional
from .response_schema import APIResponse, Metadata, Status

SUCCESS_STATUS = Status(code=200, message="Request successful")


def create_response(data: Optional[Any] = None, total_count: Optional[int] = None):
    metadata = Metadata(total_count=total_count) if total_count is not None else None
    results = [data] if data and not isinstance(data, list) else data
    return APIResponse(
        status=SUCCESS_STATUS,
        metadata=metadata,
        results=results,
    )
