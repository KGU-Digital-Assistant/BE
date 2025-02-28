from difflib import SequenceMatcher

from sqlalchemy import inspect
from typing import Type, TypeVar, Union, List, Any
from dataclasses import dataclass, asdict, fields, is_dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import BaseModel
from sqlalchemy.orm.base import instance_dict

# Generic 타입 변수
T = TypeVar("T", bound=BaseModel)
D = TypeVar("D")


def orm_to_pydantic(orm_obj: Union[object, List[object]], pydantic_model: Type[T]) -> Union[T, List[T]]:
    """
    SQLAlchemy ORM 객체를 Pydantic 모델로 변환하는 공통 함수.

    :param orm_obj: 변환할 ORM 객체 또는 ORM 객체 리스트
    :param pydantic_model: 변환할 Pydantic 모델 클래스
    :return: Pydantic 모델 객체 또는 리스트
    """
    if isinstance(orm_obj, list):  # 리스트 처리
        return [pydantic_model.model_validate(instance_dict(obj)) for obj in orm_obj]

    return pydantic_model.model_validate(instance_dict(orm_obj))  # 단일 객체 변환


def orm_to_pydantic_dataclass(orm_obj: Union[object, List[object]], pydantic_dataclass_model: Type[T]) -> Union[T, List[T]]:
    """
    SQLAlchemy ORM 객체를 Pydantic Dataclass로 변환하는 공통 함수.

    :param orm_obj: 변환할 ORM 객체 또는 ORM 객체 리스트
    :param pydantic_dataclass_model: 변환할 Pydantic Dataclass 모델 클래스
    :return: 변환된 Pydantic Dataclass 객체 또는 리스트
    """
    def convert(obj):
        data = instance_dict(obj)  # ORM 객체를 dict()로 변환

        for field_name, field_value in data.items():
            if isinstance(field_value, list):  # ✅ 리스트 필드 변환 (Many-to-One 관계)
                related_model = getattr(pydantic_dataclass_model, field_name, None)
                if related_model and hasattr(related_model, '__origin__'):  # List[Model] 타입 체크
                    item_model = related_model.__args__[0]  # List[ItemModel]에서 ItemModel 추출
                    data[field_name] = [item_model(**instance_dict(item)) for item in field_value]

            elif hasattr(field_value, "__dict__"):  # ✅ 단일 객체 변환 (One-to-One 관계)
                related_model = getattr(pydantic_dataclass_model, field_name, None)
                if related_model and issubclass(related_model, dataclass):
                    data[field_name] = related_model(**instance_dict(field_value))

        return pydantic_dataclass_model(**data)

    if isinstance(orm_obj, list):  # ✅ 리스트 변환
        return [convert(obj) for obj in orm_obj]

    return convert(orm_obj)  # ✅ 단일 객체 변환


# 공통 변환 함수
def dataclass_to_pydantic(dataclass_instance: object, pydantic_model: Type[T]) -> Any | None:
    if dataclass_instance is None:
        return None
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


def is_similar(str1: str, str2: str, threshold: float = 0.8) -> bool:
    """
    str1 과 str2 비교해서 threshold 이상 유사하면 가져옴
    """
    return SequenceMatcher(None, str1, str2).ratio() >= threshold


def row_to_dict(row) -> dict:
    return {key: getattr(row, key) for key in inspect(row).attrs.keys()}