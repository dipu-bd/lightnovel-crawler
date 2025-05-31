from typing import TypeVar, Generic, Callable, Type

T = TypeVar('T')


class static_cached_property(Generic[T]):
    def __init__(self, func: Callable[..., T]):
        self._initialized = False
        if isinstance(func, staticmethod):
            self.func = func.__func__
        else:
            self.func = func

    def __get__(self, instance: None, owner: Type) -> T:
        if not self._initialized:
            self._value = self.func()
            self._initialized = True
        return self._value
