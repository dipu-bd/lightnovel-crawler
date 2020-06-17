# -*- coding: utf-8 -*-
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
    def get_value(target: dict, path: PathType, default: dict = None) -> Union[dict, None]:
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
        keys = DictUtils.get_keys(path)
        if not keys:
            return
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        if isinstance(value, dict):
            DictUtils.merge(target, {keys[-1]: value})
        else:
            target[keys[-1]] = value
