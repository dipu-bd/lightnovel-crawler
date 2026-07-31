from collections import defaultdict
import threading
from typing import Dict, List, Tuple


class SourceHealth:
    """Per-source tally of what a crawl needed beyond a plain HTTP fetch.

    Keyed by reason rather than by a fixed set of fields so a new signal is a new
    reason string, not a schema change.
    """

    MAX_SAMPLES = 5

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._samples: Dict[Tuple[str, str], List[str]] = defaultdict(list)

    def record(self, domain: str, reason: str, detail: str = "") -> None:
        if not domain:
            return
        with self._lock:
            self._counts[domain][reason] += 1
            if not detail:
                return
            bucket = self._samples[(domain, reason)]
            if detail not in bucket and len(bucket) < self.MAX_SAMPLES:
                bucket.append(detail)

    def count(self, domain: str, reason: str) -> int:
        with self._lock:
            return self._counts.get(domain, {}).get(reason, 0)

    def reasons(self, domain: str) -> Dict[str, int]:
        with self._lock:
            return dict(self._counts.get(domain, {}))

    def tally(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            return {domain: dict(reasons) for domain, reasons in self._counts.items()}

    def samples(self, domain: str, reason: str) -> List[str]:
        with self._lock:
            return list(self._samples.get((domain, reason), ()))

    def reset(self) -> None:
        with self._lock:
            self._counts.clear()
            self._samples.clear()
