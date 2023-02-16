import asyncio
import functools
from typing import List
import typing
from .config import available_formats


def validate_formats(xs: List[str]):
    for x in xs:
        if not x in available_formats:
            return False
    return True


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
