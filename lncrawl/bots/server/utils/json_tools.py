import json
import logging
from typing import Any, TypeVar

_log = logging.getLogger(__name__)

T = TypeVar('T')


def json_encode(data: Any, encoding: str = "utf-8") -> bytes:
    try:
        output = json.dumps(
            data,
            allow_nan=True,
            ensure_ascii=False,
            check_circular=True,
            separators=(',', ':'),
        )
        return output.encode(encoding)
    except Exception as err:
        _log.debug('Failed encoding', err)
        return b''


def json_decode(data: str | bytes | bytearray | None, _default: T) -> T:
    try:
        if isinstance(data, bytearray):
            data = bytes(data)
        if isinstance(data, bytes):
            data = data.decode()
        if not isinstance(data, str):
            return _default
        return json.loads(data)
    except Exception as err:
        _log.debug('Failed decoding', err)
        return _default
