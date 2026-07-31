"""The one URL helper scraper does not provide.

The other three — ``extract_base``, ``extract_host`` and ``validate_url`` — used to live
here too, duplicating scraper's. Diffed over all 515 URLs in the source index the two
agreed on every one, and disagreed only where this copy crashed or produced ``:///``,
so nothing stored was ever keyed by the difference and taking scraper's needed no
migration.
"""

from .text_tools import normalize


def normalize_url(url: str) -> str:
    """Normalizes the URL string"""
    return normalize(url).encode("idna").decode("ascii")
