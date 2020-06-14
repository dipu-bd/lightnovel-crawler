# -*- coding: utf-8 -*-
import re
from typing import Any, List, Set, Tuple, Union

PathType = Union[str, List[str], Tuple[str], Set[str]]


class DictUtils:
    sep = '/'

    @staticmethod
    def merge(target: dict, *sources: dict) -> dict:
        for source in sources:
            if isinstance(source, dict):
                for key, val in source.items():
                    if key in target \
                            and isinstance(val, dict) \
                            and isinstance(target[key], dict):
                        target[key] = DictUtils.merge(target[key], val)
                    else:
                        target[key] = val
        return target

    @staticmethod
    def get_keys(path: PathType) -> List[str]:
        keys = []
        if isinstance(path, str):
            keys += path.split(DictUtils.sep)
        else:
            for sub in path:
                if isinstance(sub, str):
                    keys += sub.split(DictUtils.sep)
        return list(filter(None, keys))

    @staticmethod
    def has_path(target: dict, path: PathType) -> bool:
        keys = DictUtils.get_keys(path)
        if len(keys) > 0:
            for key in keys:
                if key not in target:
                    return False
                target = target[key]
            return True
        return False

    @staticmethod
    def resolve(target: dict, path: PathType, default: Any = None) -> dict:
        keys = DictUtils.get_keys(path)
        if len(keys) > 0:
            for key in keys:
                if key not in target:
                    return default
                target = target[key]
            return target
        return default

    @staticmethod
    def put_value(target: dict, path: PathType, value: Any) -> None:
        if len(path) > 0:
            for key in path[:-1]:
                target = target.setdefault(key, {})
            merge(target, {path[-1]: value})
        elif isinstance(value, dict):
            merge(target, value)
        else:
            raise ValueError("Expected non-empty path or a 'dictionary' value;" +
                             f"Got empty path and a '{type(value)}' value")
