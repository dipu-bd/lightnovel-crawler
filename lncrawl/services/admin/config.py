from __future__ import annotations

from functools import cached_property, lru_cache
import inspect
import re
import sys
from typing import (
    Annotated,
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from ...config import Hidden, Sensitive, _deserialize, _Section, _serialize
from ...context import ctx
from ...exceptions import ServerErrors
from ...server.models import ConfigProperty, ConfigSection


def _unwrap_return_type(annotation: Any) -> Any:
    origin = get_origin(annotation)
    is_union = origin is Union
    if sys.version_info >= (3, 10):
        from types import UnionType

        is_union = is_union or origin is UnionType
    if is_union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        return args[0] if len(args) == 1 else annotation
    return annotation


def _strip_annotated_sensitive(annotation: Any) -> Tuple[Any, bool, bool]:
    """Remove all ``Annotated`` wrappers and detect the marker classes."""
    sensitive = False
    hidden = False

    def peel(a: Any) -> Any:
        nonlocal sensitive, hidden
        while a is not None and get_origin(a) is Annotated:
            args = get_args(a)
            if not args:
                break
            for meta in args[1:]:
                if meta is Sensitive:
                    sensitive = True
                elif meta is Hidden:
                    hidden = True
            a = args[0]
        return a

    ann = peel(annotation)
    ann = _unwrap_return_type(ann)
    ann = peel(ann)
    return ann, sensitive, hidden


def _value_kind_for_annotation(annotation: Any) -> str:
    if annotation is None:
        return "any"
    ann = _unwrap_return_type(annotation)
    if ann is str:
        return "string"
    if ann is int or ann is float:
        return "number"
    if ann is bool:
        return "boolean"
    return "any"


def _humanize_key(name: str) -> str:
    return re.sub(r"_+", " ", name).strip().title()


def _parse_property_doc(doc: Optional[str], attr_name: str) -> Tuple[str, str]:
    if not doc or not doc.strip():
        return _humanize_key(attr_name), ""
    text = inspect.cleandoc(doc)
    parts = re.split(r"\n\s*\n", text, maxsplit=1)
    display = parts[0].strip().rstrip(".")
    description = parts[1].strip() if len(parts) > 1 else ""
    return display or _humanize_key(attr_name), description


def _get_value_kind(attr: property) -> Tuple[str, bool, bool]:
    anns = get_type_hints(attr.fget, include_extras=True)
    return_type = anns.get("return")
    if return_type is None:
        return "any", False, False
    bare_return, is_sensitive, is_hidden = _strip_annotated_sensitive(return_type)
    value_kind = _value_kind_for_annotation(bare_return)
    return value_kind, is_sensitive, is_hidden


def _get_masked_value(value: Any) -> Any:
    str_value = str(value or "")
    if not str_value:
        return ""
    mask = "********"
    cl = min(4, len(str_value) // 8)
    if cl > 0:
        return str_value[:cl] + mask + str_value[-cl:]
    return mask


def _get_properties(section: _Section) -> Iterable[ConfigProperty]:
    for name in dir(section):
        if name.startswith("_"):
            continue
        attr = getattr(type(section), name, None)
        if isinstance(attr, property) and attr.fset:
            value_kind, is_sensitive, is_hidden = _get_value_kind(attr)
            if is_hidden:
                continue
            value = _serialize(getattr(section, name))
            display, description = _parse_property_doc(attr.fget.__doc__, name)
            if is_sensitive:
                value = _get_masked_value(value)
            yield ConfigProperty(
                key=name,
                value=value,
                value_kind=value_kind,
                display_name=display,
                description=description,
                sensitive=is_sensitive,
            )


def _get_sections() -> Iterable[ConfigSection]:
    for name in dir(ctx.config):
        if name.startswith("_"):
            continue
        attr = getattr(type(ctx.config), name, None)
        if isinstance(attr, cached_property):
            value = getattr(ctx.config, name)
            if isinstance(value, _Section):
                properties = list(_get_properties(value))
                display, description = _parse_property_doc(attr.__doc__, name)
                yield ConfigSection(
                    key=name,
                    display_name=display,
                    description=description,
                    properties=properties,
                )


@lru_cache(maxsize=1)
def list_config_sections() -> List[ConfigSection]:
    return list(_get_sections())


def update_config(section_key: str, property_key: str, value: Any, dry_run: bool = False) -> None:
    section = getattr(ctx.config, section_key)
    current_value = getattr(section, property_key)
    new_value = _deserialize(value, type(current_value))
    if current_value == new_value:
        return
    if not dry_run:
        try:
            setattr(section, property_key, new_value)
        except ValueError as e:
            # A setter that validates its range is the only thing standing between the
            # settings page and a value that breaks every crawler at once, so the
            # rejection has to read as a rejection rather than as a server fault.
            raise ServerErrors.invalid_input.with_extra(str(e))
