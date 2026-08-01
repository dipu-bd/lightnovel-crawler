"""What a scraper failure means *here*, in terms an operator can act on.

The scraper says what happened and what the binding detection layer reads. Neither
sentence knows what this application can offer, so neither can finish the thought — and
"what would help" is the only part of a diagnosis a person can act on. That is the split:
:mod:`scraper.failure` owns the objective half, and every string below names something
lncrawl actually has — a crawler setting, a proxy list, a browser toggle. A library
asserting them would be wrong for the next consumer.

Two functions rather than one on purpose. :func:`describe` is prose for a person,
:func:`diagnosis_extra` is fields for the API, and folding them together would leave the
endpoint re-deriving structure by parsing an English sentence.
"""

from typing import Any, Dict

from scraper import (
    LAYERS,
    Stance,
    blocking_layer,
    failure_kind,
    is_permanent,
    reads,
    status_code,
    status_note,
    summarise,
)
from scraper.failure import RENDER_FAILED, SOLVE_FAILED

# Where lncrawl reads more into a status code than a library may. That a 404 means a
# source's URL scheme has changed is true of a novel site and not of the web, so the
# scraper states the code plainly and this replaces the whole sentence rather than
# appending to it. Keyed off `status_note` rather than its text: if the scraper rephrases,
# the override still lands, and lncrawl's wording is meant to win either way.
_STATUS_INFERENCE = {
    404: "The page is not there — this source's URLs have almost certainly changed.",
}

# What to do about a failure the layer model has nothing to say about, because the site
# did not cause it. Keyed by kind rather than by stance for exactly that reason: our own
# browser came back empty-handed, and no amount of knowing what the site reads helps.
_ADVICE = {
    RENDER_FAILED: (
        "Either the element this source waits for never appears, or the page needs longer"
        " than the render timeout allows. A selector that matches the page shell rather"
        " than its content is the usual cause."
    ),
    SOLVE_FAILED: (
        "Check that a browser is installed and able to open a window, and that the solve"
        " timeout leaves it enough time. This is a local capability failing, not the site"
        " refusing us."
    ),
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
    Stance.DELEGATE: (
        "the only tier above this one is a paid per-request service, which lncrawl does"
        " not integrate — so there is nothing here to configure and this source is past"
        " what the stack reaches"
    ),
    Stance.REFUSE: "there is no bypass; this content needs credentials or a registered agent",
}


def describe(error: BaseException, *, url: str = "") -> str:
    """One legible paragraph: what happened, what caused it, what would help."""
    parts = summarise(error, url=url)

    code = status_code(error)
    inference = _STATUS_INFERENCE.get(code) if code is not None else None
    if inference:
        note = status_note(code)
        parts = [inference if part == note else part for part in parts]

    layer = blocking_layer(error)
    facts = LAYERS.get(layer) if layer is not None else None
    if facts is not None:
        parts.append(f"It reads {reads(facts.trait)}, so {_REMEDY[facts.stance]}.")

    advice = _ADVICE.get(failure_kind(error))
    if advice:
        parts.append(advice)

    return "\n".join(parts)


def diagnosis_extra(error: BaseException) -> Dict[str, Any]:
    """Structured fields for `Job.extra`, so nothing has to parse the prose."""
    layer = blocking_layer(error)
    facts = LAYERS.get(layer) if layer is not None else None
    return {
        "failure_kind": failure_kind(error),
        "failure_detail": getattr(error, "detail", "") or str(error),
        "failure_url": getattr(error, "url", "") or "",
        "status_code": status_code(error),
        "is_permanent": is_permanent(error),
        "blocking_layer": int(layer) if layer is not None else None,
        "blocking_layer_name": str(layer) if layer is not None else None,
        "reads": facts.trait.value if facts is not None else None,
        "stance": facts.stance.value if facts is not None else None,
    }
