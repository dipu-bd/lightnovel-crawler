from typing import TypeVar, Generic, Callable

T = TypeVar('T')


class static_cached_property(Generic[T]):
    def __init__(self, func: Callable[..., T]):
        self.func = func
        self._initialized = False

    def __get__(self, instance, owner) -> T:
        if not self._initialized:
            self._value = self.func()
            self._initialized = True
        return self._value
