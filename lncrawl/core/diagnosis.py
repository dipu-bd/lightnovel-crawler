"""What a scraper failure means, in terms an operator can act on.

The scraper attributes a retrieval failure to the detection layer it believes is
binding, and every layer carries two static facts: what it *reads*, and what this
stack will do about it. Those two answer the question a status code cannot — whether
there is anything a human could change — which is the whole reason a diagnosis is
worth surfacing instead of a traceback.

Four functions rather than one on purpose. :func:`describe` is prose for a person,
:func:`diagnosis_extra` is fields for the API, and folding them together would leave
the endpoint re-deriving structure by parsing an English sentence.
"""

from typing import Any, Dict, Optional

from PIL import UnidentifiedImageError
from requests import HTTPError, RequestException
from scraper import LAYERS, Layer, Stance, Trait
from scraper.exceptions import (
    Aborted,
    Blocked,
    Exhausted,
    Impassable,
    MissingDependency,
    Poisoned,
    TierUnavailable,
)

BLOCKED = "blocked"
UNREACHABLE = "unreachable"
EXHAUSTED = "exhausted"
IMPASSABLE = "impassable"
POISONED = "poisoned"
TIER_UNAVAILABLE = "tier_unavailable"
MISSING_DEPENDENCY = "missing_dependency"
HTTP_ERROR = "http_error"
BAD_IMAGE = "bad_image"
ABORTED = "aborted"
FAILED = "failed"

_HEADLINE = {
    IMPASSABLE: "The site requires something no scraper can fabricate",
    EXHAUSTED: "Every bypass this configuration reaches was tried and the site still refused",
    BLOCKED: "The site refused the request",
    UNREACHABLE: "The request never reached the site",
    POISONED: "A page came back, but its content looks like decoy filler",
    TIER_UNAVAILABLE: "No configured capability can serve this request",
    MISSING_DEPENDENCY: "An optional dependency is needed and is not installed",
    HTTP_ERROR: "The site answered with an error",
    BAD_IMAGE: "What the site served in place of an image could not be decoded",
    ABORTED: "The request was aborted",
    FAILED: "The request failed",
}

# What a status code says about the source itself, for the codes that survive the
# retrieval ladder. Anything the ladder diagnoses arrives as a `Blocked` instead, so a
# code reaching here is the site's plain answer rather than a mitigation verdict.
_STATUS_HINT = {
    404: "The page is not there — this source's URLs have almost certainly changed.",
    410: "The page is gone for good, as the site states outright.",
    451: "The site withholds this page for legal reasons.",
}

_READS = {
    Trait.EMIT: "bytes the client chooses to send, which can be reproduced",
    Trait.POSSESS: "something the client must genuinely hold, which cannot be forged",
    Trait.HYBRID: "an artifact bound to something held, so sending the right bytes is not enough",
    Trait.OUTSIDE: "behaviour over time rather than the request itself",
}

_REMEDY = {
    Stance.SATISFY: (
        "the request signature is what has to change, which is the scraper's own work"
        " and not a setting here"
    ),
    Stance.LEASE: (
        "only a better address helps — configure a proxy or a tor-pool in the crawler settings"
    ),
    Stance.ACCUMULATE: (
        "the site is measuring history, so giving this source a slower rate limit helps"
        " and changing address does not"
    ),
    Stance.SOLVE: (
        "a real browser clears this once per site — check that browser crawling is"
        " enabled and a browser is installed"
    ),
    Stance.AVOID: "there is nothing to defeat here; the source should not be asking for what tripped it",
    Stance.DELEGATE: "this is past what lncrawl will attempt on its own",
    Stance.REFUSE: "there is no bypass; this content needs credentials or a registered agent",
}


def kind(error: BaseException) -> str:
    """A short, stable name for the class of failure.

    Doubles as the source-health reason, so the tally an admin reads and the field
    the API returns cannot drift apart.
    """
    if isinstance(error, Impassable):
        return IMPASSABLE
    if isinstance(error, Exhausted):
        return EXHAUSTED
    if isinstance(error, Blocked):
        return BLOCKED if error.layer is not None else UNREACHABLE
    if isinstance(error, Poisoned):
        return POISONED
    if isinstance(error, MissingDependency):
        return MISSING_DEPENDENCY
    if isinstance(error, TierUnavailable):
        return TIER_UNAVAILABLE
    if isinstance(error, Aborted):
        return ABORTED
    if isinstance(error, HTTPError):
        return HTTP_ERROR
    if isinstance(error, UnidentifiedImageError):
        return BAD_IMAGE
    if isinstance(error, RequestException):
        return UNREACHABLE
    return FAILED


def status_code(error: BaseException) -> Optional[int]:
    """The status the site answered with, when it answered at all."""
    response = getattr(error, "response", None)
    code = getattr(response, "status_code", None)
    return code if isinstance(code, int) else None


def blocking_layer(error: BaseException) -> Optional[Layer]:
    """The layer this failure is attributed to, never a status code.

    ``None`` covers three separate things and deliberately does not tell them apart:
    not a scraper failure at all, one the model declined to attribute, and one that is
    ours rather than the site's. To a caller they mean the same thing — there is no
    layer to look up.
    """
    layer = getattr(error, "layer", None)
    return layer if isinstance(layer, Layer) else None


def is_permanent(error: BaseException) -> bool:
    """Whether asking again, unchanged, cannot succeed.

    True where the binding layer reads a secret, and for content already recorded as
    decoy. Deliberately false for `Exhausted`, which says every tier *this*
    configuration reaches was spent — a proxy, a browser or the archive may still get
    through, so treating it as permanent would retire a source over a setting.
    """
    return isinstance(error, (Impassable, Poisoned))


def describe(error: BaseException, *, url: str = "") -> str:
    """One legible paragraph: what happened, what caused it, what would help."""
    where = url or getattr(error, "url", "") or ""
    parts = [_HEADLINE.get(kind(error), _HEADLINE[FAILED])]
    code = status_code(error)
    if code is not None:
        parts[0] += f" (HTTP {code})"
    if where:
        parts[0] += f" for {where}"

    # `str()` only where there is no `detail`: a scraper failure that carries one has
    # already folded the layer and the URL into its message, so using it here would
    # repeat both of the lines around it.
    detail = getattr(error, "detail", "") or ""
    if not detail and not hasattr(error, "detail"):
        detail = str(error)
    if detail:
        parts.append(f"{detail}.")

    hint = _STATUS_HINT.get(code) if code is not None else None
    if hint:
        parts.append(hint)

    layer = blocking_layer(error)
    facts = LAYERS.get(layer) if layer is not None else None
    if facts is not None:
        parts.append(f"{layer} — {facts.summary}")
        parts.append(f"It reads {_READS[facts.trait]}, so {_REMEDY[facts.stance]}.")
    elif isinstance(error, Blocked):
        parts.append(
            "Nothing identified this as bot mitigation, so no layer was attributed and"
            " there is no remedy to recommend: either the site's own server failed to"
            " answer, or the fault is at this end — a proxy that refused its credentials,"
            " an address with no route."
        )

    return "\n".join(parts)


def diagnosis_extra(error: BaseException) -> Dict[str, Any]:
    """Structured fields for `Job.extra`, so nothing has to parse the prose."""
    layer = blocking_layer(error)
    facts = LAYERS.get(layer) if layer is not None else None
    return {
        "failure_kind": kind(error),
        "failure_detail": getattr(error, "detail", "") or str(error),
        "failure_url": getattr(error, "url", "") or "",
        "status_code": status_code(error),
        "is_permanent": is_permanent(error),
        "blocking_layer": int(layer) if layer is not None else None,
        "blocking_layer_name": str(layer) if layer is not None else None,
        "reads": facts.trait.value if facts is not None else None,
        "stance": facts.stance.value if facts is not None else None,
    }
