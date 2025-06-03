from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    total: int
    offset: int
    limit: int
    items: List[T]
