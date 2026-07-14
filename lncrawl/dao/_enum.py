from enum import Enum
from typing import Any, Optional, Type

import sqlalchemy as sa


class IntEnumType(sa.types.TypeDecorator):
    """Persist an ``IntEnum`` by its integer value instead of a native DB enum.

    Reads always return the enum member. It is tolerant of legacy rows that
    stored the member *name* as a string (the pre-migration representation), so
    an in-place upgrade never breaks reads before the values are normalized.
    """

    impl = sa.SmallInteger
    cache_ok = True

    def __init__(self, enum_class: Type[Enum], **kwargs: Any) -> None:
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[int]:
        if value is None:
            return None
        return int(self._coerce(value).value)

    def process_result_value(self, value: Any, dialect: Any) -> Optional[Enum]:
        if value is None:
            return None
        return self._coerce(value)

    def _coerce(self, value: Any) -> Enum:
        if isinstance(value, self.enum_class):
            return value
        try:
            return self.enum_class(int(value))
        except (ValueError, TypeError):
            # Legacy value stored the member name as a string.
            return self.enum_class[str(value)]
