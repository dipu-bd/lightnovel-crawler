"""The configured ways out, as data rather than as a string.

Kept out of `config.py` so the property there stays a getter and a docstring, and out of
the server models so the configuration does not depend on the API layer.
"""

from enum import Enum
from hashlib import md5
from typing import Any, List, Optional
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

DEFAULT_TORPOOL_SOCKS = "socks5h://127.0.0.1:9250"
DEFAULT_TORPOOL_API = "http://127.0.0.1:8080"


class ProxyKind(str, Enum):
    """What an address looks like to a reputation database.

    Only `isp`, `residential` and `mobile` get past a site that blocks on reputation.
    Datacenter ranges and Tor exit lists are both published, so neither clears one.
    `torpool` is a tor-pool endpoint — many Tor instances behind one sticky port — and
    scores as Tor for exactly that reason, but it is the only form that can rotate.
    """

    datacenter = "datacenter"
    isp = "isp"
    residential = "residential"
    mobile = "mobile"
    tor = "tor"
    torpool = "torpool"


class ProxyExit(BaseModel):
    """One configured way out.

    Carries an `id` because this is an editable list: rows are reordered and deleted, so
    matching a submitted entry to the stored one it came from cannot rely on position,
    and cannot rely on the URL either — that is the field whose password is elided on
    the way out.
    """

    id: str = Field(default_factory=lambda: uuid4().hex, description="Stable row identity")
    url: str = Field(default="", description="Proxy URL, e.g. socks5h://host:1080")
    kind: ProxyKind = Field(default=ProxyKind.datacenter, description="What kind of address")
    label: str = Field(default="", description="Name shown in logs and the exit status view")
    enabled: bool = Field(default=True, description="Uncheck to keep an entry without using it")
    api_url: str = Field(default="", description="tor-pool API URL; tor-pool entries only")
    token: str = Field(default="", description="tor-pool proxy-scoped token")

    @model_validator(mode="after")
    def _check(self) -> "ProxyExit":
        if not self.url.strip():
            raise ValueError("a proxy entry needs a URL")
        if "://" not in self.url:
            raise ValueError(f"proxy URL needs a scheme: {self.url!r}")
        if self.kind is ProxyKind.torpool and not self.api_url.strip():
            raise ValueError("a tor-pool entry needs its API URL")
        return self

    @property
    def name(self) -> str:
        """What to call this exit where its URL must not appear."""
        return self.label or urlsplit(self.url).hostname or self.url


def mask_url(url: str) -> str:
    """The same URL with its password replaced.

    A proxy URL routinely carries `user:pass@`, and these are read back by a settings
    page. Only the password goes: the user and host are what make one entry
    recognisable from another.
    """
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    if not parts.password:
        return url
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    netloc = f"{parts.username}:***@{host}" if parts.username else f"***@{host}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def _stable_id(entry: str) -> str:
    """An id derived from the legacy text rather than minted.

    The import runs on every read until something is saved through the structured path,
    so a random id would differ between two reads of the same configuration — and the
    id is what matches a submitted entry back to the stored one whose secrets were
    elided. Same text, same row.
    """
    return md5(entry.encode("utf-8")).hexdigest()[:16]


def from_legacy(value: str) -> List[ProxyExit]:
    """Read the comma-separated string that `proxy_urls` used to hold.

    Frozen on purpose. It reads the three forms that existed before proxies became
    structured and will not grow a fourth — new configuration is written as data. It
    stays because `PROXY_URLS` in the environment is inherently a string, and because
    an installation upgrading from an older version has one of these stored.

    An entry that cannot be read is skipped rather than raised on: this runs while the
    configuration is being loaded, and one bad entry must not stop the app starting.
    """
    exits: List[ProxyExit] = []
    for entry in (value or "").split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = [p.strip() for p in entry.split(";")]
        try:
            if parts[0] == "torpool":
                # torpool;<api_url>;<socks_url>;<token>
                exits.append(
                    ProxyExit(
                        id=_stable_id(entry),
                        kind=ProxyKind.torpool,
                        url=(parts[2] if len(parts) > 2 and parts[2] else DEFAULT_TORPOOL_SOCKS),
                        api_url=(parts[1] if len(parts) > 1 and parts[1] else DEFAULT_TORPOOL_API),
                        token=parts[3] if len(parts) > 3 else "",
                    )
                )
            elif parts[0] == "tor":
                # tor;<host>;<port>;<control_port>;<control_password>, the last two
                # accepted and ignored since rotation by NEWNYM is gone.
                host = parts[1] if len(parts) > 1 and parts[1] else "127.0.0.1"
                port = parts[2] if len(parts) > 2 and parts[2] else "9050"
                exits.append(
                    ProxyExit(
                        id=_stable_id(entry),
                        kind=ProxyKind.tor,
                        url=f"socks5h://{host}:{port}",
                    )
                )
            else:
                exits.append(ProxyExit(id=_stable_id(entry), kind=ProxyKind.datacenter, url=entry))
        except ValueError:
            continue
    return exits


def load(stored: Any, legacy: str = "") -> List[ProxyExit]:
    """The configured exits, importing *legacy* when nothing structured is stored."""
    if isinstance(stored, list):
        out: List[ProxyExit] = []
        for item in stored:
            if isinstance(item, ProxyExit):
                out.append(item)
            elif isinstance(item, dict):
                try:
                    out.append(ProxyExit(**item))
                except ValueError:
                    continue
        return out
    return from_legacy(legacy)


def dump(value: Any) -> List[dict]:
    """Normalise whatever a caller assigned into storable dicts, validating each.

    A plain string is still accepted and read as the legacy form, so the environment
    variable and an older client both keep working.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [item.model_dump(mode="json") for item in from_legacy(value)]
    items: List[ProxyExit] = []
    for item in value:
        items.append(item if isinstance(item, ProxyExit) else ProxyExit(**item))
    return [item.model_dump(mode="json") for item in items]


def find(exits: List[ProxyExit], name: str) -> Optional[ProxyExit]:
    """The exit a status entry refers to, matched on the name it reports."""
    for item in exits:
        if item.name == name:
            return item
    return None


def public(item: ProxyExit) -> dict:
    """One entry as it may be read back: no token, and no password in the URL."""
    return {
        "id": item.id,
        "url": mask_url(item.url),
        "kind": item.kind.value,
        "label": item.label,
        "enabled": item.enabled,
        "api_url": item.api_url,
        "has_token": bool(item.token),
    }


def merge_secrets(submitted: List[ProxyExit], existing: List[ProxyExit]) -> List[ProxyExit]:
    """Put back the secrets that were never sent out.

    A client edits what it was given, and what it was given had the token removed and the
    URL's password replaced. Echoing that back would save the elision over the real value
    — so an entry whose secret still looks elided keeps whatever the stored entry of the
    same id had, and anything actually typed wins.
    """
    by_id = {item.id: item for item in existing}
    out: List[ProxyExit] = []
    for item in submitted:
        prior = by_id.get(item.id)
        if prior is not None:
            if not item.token:
                item = item.model_copy(update={"token": prior.token})
            if mask_url(prior.url) == item.url and prior.url != item.url:
                item = item.model_copy(update={"url": prior.url})
        out.append(item)
    return out
