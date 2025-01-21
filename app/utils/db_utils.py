from sqlalchemy import inspect
from typing import Type, TypeVar
from dataclasses import dataclass, asdict, fields, is_dataclass
from pydantic import BaseModel

# Generic 타입 변수
T = TypeVar("T", bound=BaseModel)
D = TypeVar("D")


# 공통 변환 함수
def dataclass_to_pydantic(dataclass_instance: object, pydantic_model: Type[T]) -> T:
    data = asdict(dataclass_instance)
    pydantic_fields = pydantic_model.__annotations__.keys()
    filtered_data = {key: value for key, value in data.items() if key in pydantic_fields}
    return pydantic_model(**filtered_data)


def pydantic_to_dataclass(pydantic_instance: BaseModel, dataclass_model: Type[D]) -> D:
    if not is_dataclass(dataclass_model):
        raise ValueError(f"{dataclass_model} is not a dataclass")

    data = pydantic_instance.dict()
    dataclass_fields = {field.name for field in fields(dataclass_model)}
    filtered_data = {key: value for key, value in data.items() if key in dataclass_fields}
    return dataclass_model(**filtered_data)


def row_to_dict(row) -> dict:
    return {key: getattr(row, key) for key in inspect(row).attrs.keys()}