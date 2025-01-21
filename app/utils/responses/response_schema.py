from pydantic import BaseModel
from typing import Generic, List, Optional, TypeVar, Any

T = TypeVar("T")


class Status(BaseModel):
    code: int
    message: str


class Metadata(BaseModel):
    total_count: int


class APIResponse(BaseModel, Generic[T]):
    status: Status
    metadata: Optional[Metadata] = None
    results: Optional[List[T]] = None

