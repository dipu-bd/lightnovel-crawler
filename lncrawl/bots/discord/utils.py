import asyncio
import functools
import typing as t
from .config import available_formats


def validate_formats(xs: t.List[str]):
    for x in xs:
        if not x in available_formats:
            return False
    return True


def to_thread(func: t.Callable) -> t.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
