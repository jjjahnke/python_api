from enum import Enum
from pydantic import BaseModel


class TestEnum(str, Enum):
    foo = "foo"
    bar = "bar"


class NestedModel(BaseModel):
    class TestModel(BaseModel):
        name: str
        age: int
        enum: TestEnum

    test: list[TestModel]
