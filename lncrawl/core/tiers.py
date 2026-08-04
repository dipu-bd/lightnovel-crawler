"""Which tier a source comes from, and what that means for stored content.

While declarative specs and Python crawlers both exist, a host may be served by either. Two
rules follow, and both are easy to get wrong in a way nothing reports.

**Precedence is by tier, never by version.** A source's version is a timestamp, so a legacy
crawler re-downloaded by the sync gets a fresh one and would outrank the spec meant to replace
it, intermittently and depending on file modification times.

**Staleness needs positive evidence.** A version is also a cache key: stored chapters are
re-downloaded when it changes. A host moving from one tier to the other changes the value
without changing the content, and treating that as staleness would make every user's library
look stale at once, with nothing about the symptom pointing here.
"""

from pathlib import Path
from typing import Any, Dict, Mapping, Optional

__all__ = [
    "LEGACY",
    "SPEC",
    "TIERS",
    "describe",
    "outranks",
    "rank",
    "stamp",
    "stored_version",
    "is_stale",
]

#: A declarative spec from the definitions repository.
SPEC = "spec"

#: A Python crawler from the bundled corpus or the user's own directory.
LEGACY = "legacy"

#: Highest precedence first.
TIERS = (SPEC, LEGACY)

#: Where a stamp records what produced some stored content.
VERSION_KEY = "crawler_version"
TIER_KEY = "crawler_tier"


def describe(tier: Optional[str], path: Any = None) -> str:
    """Which tier serves a host and from what file, for a log line.

    The file name alone, because the extension already separates the tiers and a full path
    from the data directory buries the answer the line exists to give.
    """
    # Absent means legacy, as everywhere else here: content and crawlers predating tiers.
    known = tier or LEGACY
    label = known if known in TIERS else f"unknown tier {tier!r}"
    name = Path(str(path)).name if path else ""
    return f"{label} ({name})" if name else label


def rank(tier: Optional[str]) -> int:
    """How strongly a tier claims a host. Lower wins."""
    try:
        return TIERS.index(tier or LEGACY)
    except ValueError:
        # An unknown tier loses to everything known rather than winning by accident.
        return len(TIERS)


def outranks(tier: Optional[str], version: Any, other_tier: Optional[str], other: Any) -> bool:
    """Whether (*tier*, *version*) should replace (*other_tier*, *other*).

    Tier decides first. Version only breaks a tie within one tier, which is what stops a
    re-synced legacy crawler from displacing a spec.
    """
    mine, theirs = rank(tier), rank(other_tier)
    if mine != theirs:
        return mine < theirs
    return _as_number(version) >= _as_number(other)


def _as_number(value: Any) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return -1.0


def stamp(extra: Optional[Mapping[str, Any]], version: Any, tier: str = LEGACY) -> Dict[str, Any]:
    """Record what produced this content, alongside whatever else *extra* holds."""
    out: Dict[str, Any] = dict(extra or {})
    out[VERSION_KEY] = None if version is None else str(version)
    out[TIER_KEY] = tier
    return out


def stored_version(extra: Optional[Mapping[str, Any]]) -> Optional[str]:
    """The version stamped on stored content, as a string, or None when there is none.

    Older content was stamped with an integer, so this normalises rather than assuming. Reading
    it as a string is what lets the value become a digest without a comparison silently failing
    for every chapter ever stored.
    """
    if not extra:
        return None
    value = extra.get(VERSION_KEY)
    if value is None or value == "":
        return None
    return str(value)


def stored_tier(extra: Optional[Mapping[str, Any]]) -> str:
    """The tier stamped on stored content. Content stamped before tiers existed is legacy."""
    if not extra:
        return LEGACY
    return str(extra.get(TIER_KEY) or LEGACY)


def is_stale(extra: Optional[Mapping[str, Any]], version: Any, tier: str = LEGACY) -> bool:
    """Whether stored content was produced by something other than this crawler.

    Deliberately conservative. It answers True only with evidence: the same tier, both versions
    known, and different. Anything else is "unknown", and unknown must not invalidate, because
    a needless re-download of a whole library is far worse than serving one stale chapter.
    """
    if stored_tier(extra) != tier:
        # The host moved tiers. Equivalence was verified before the spec was adopted, so the
        # content is fine and re-downloading it would be pure cost.
        return False

    stored = stored_version(extra)
    if stored is None:
        return False
    if version is None:
        return False
    return stored != str(version)
