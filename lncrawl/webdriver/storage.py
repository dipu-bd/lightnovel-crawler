import json
from typing import (
    TYPE_CHECKING,
    Any,
    ItemsView,
    Iterator,
    KeysView,
    Literal,
    MutableMapping,
    Optional,
)

if TYPE_CHECKING:
    from ..core.browser import Browser

__all__ = ["BrowserStorage"]


class BrowserStorage(MutableMapping[str, Optional[str]]):
    def __init__(
        self,
        browser: "Browser",
        source: Literal["localStorage", "sessionStorage"] = "localStorage",
    ):
        self._source = source
        self._browser = browser

    def __repr__(self) -> str:
        return f"BrowserStorage({self._source})"

    def __len__(self) -> int:
        return self.length

    def __contains__(self, key) -> bool:
        return self.has(str(key))

    def __getitem__(self, key: str) -> Optional[str]:
        return self.get(key)

    def __setitem__(self, key: str, value: Optional[str]) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.remove(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    @property
    def raw(self) -> MutableMapping[str, Optional[str]]:
        js = f"return {{...window.{self._source}}}"
        return self._browser.execute_js(js) or {}

    @property
    def length(self) -> int:
        js = f"return window.{self._source}.length;"
        return self._browser.execute_js(js) or 0

    def items(self) -> ItemsView[str, Optional[str]]:
        return self.raw.items()

    def keys(self) -> KeysView[str]:
        js = f"return Object.keys(window.{self._source});"
        result = self._browser.execute_js(js) or []
        return set(result)  # type: ignore[return-value]

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        key_js = json.dumps(key)
        js = f"return window.{self._source}.getItem({key_js});"
        value = self._browser.execute_js(js)
        return str(value) if value is not None else default

    def set(self, key: str, value: Any) -> None:
        key_js = json.dumps(key)
        val_js = json.dumps(str(value))
        js = f"window.{self._source}.setItem({key_js}, {val_js}); return true;"
        if not self._browser.execute_js(js):
            raise RuntimeError(f"Failed to set {key} in {self._source}")

    def has(self, key: str) -> bool:
        key_js = json.dumps(key)
        js = f"return window.{self._source}.hasOwnProperty({key_js});"
        return self._browser.execute_js(js) or False

    def remove(self, key: str) -> None:
        key_js = json.dumps(key)
        js = f"window.{self._source}.removeItem({key_js}); return true;"
        if not self._browser.execute_js(js):
            raise RuntimeError(f"Failed to remove {key} from {self._source}")

    def clear(self) -> None:
        js = f"window.{self._source}.clear(); return true;"
        if not self._browser.execute_js(js):
            raise RuntimeError(f"Failed to clear {self._source}")
