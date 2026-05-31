from collections import Counter, OrderedDict
import heapq
import logging
import math
import re
import threading
import time
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple

import sqlmodel as sq

from ..context import ctx
from ..dao import Novel
from ..exceptions import ServerErrors

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tunable knobs
# ---------------------------------------------------------------------------

# Scoring weights
WEIGHT_TITLE = 50  # IDF-weighted Jaccard² title overlap × this value
WEIGHT_TAGS = 40  # plain Jaccard tag overlap × this value
WEIGHT_AUTHOR = 30  # flat bonus when candidate shares at least one author
WEIGHT_DOMAIN = 20  # flat bonus when candidate shares the same source domain

# Candidate pool limits per phase
TITLE_CANDIDATE_LIMIT = 400  # max title-similar candidates from the inverted index
PHASE2_DOMAIN_LIMIT = 100  # max same-domain candidates fetched
MIN_WORD_LENGTH = 3  # title words shorter than this are skipped in index lookups

# Cache settings
CACHE_MAX_ENTRIES = 10000  # max novels cached simultaneously (LRU eviction after this)
CACHE_TTL_SECONDS = 7200  # absolute expiry: entries older than 2 h are evicted
CACHE_RESULTS = 20  # top-N IDs stored per entry; any limit ≤ this is free
FRESH_TTL_SECONDS = 3600  # entries older than 1 h trigger a background refresh

# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-z0-9]+")

# Columns needed for scoring — avoids fetching synopsis, cover_url, etc.
_SCORE_COLS = (Novel.id, Novel.tags, Novel.domain, Novel.title, Novel.authors)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _words(text: str) -> Set[str]:
    """Lowercase alphanumeric tokens — strips punctuation."""
    return set(_WORD_RE.findall(text.lower()))


def _author_set(authors: Optional[str]) -> Set[str]:
    """Split a comma-separated authors string into a lowercase set."""
    if not authors:
        return set()
    return {a.strip().lower() for a in authors.split(",") if a.strip()}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _idf_jaccard(a: Set[str], b: Set[str], idf: Dict[str, float]) -> float:
    """IDF-weighted Jaccard: rare words contribute more than common words."""
    union = a | b
    if not union:
        return 0.0
    intersection = a & b
    w_intersection = sum(idf.get(w, 1.0) for w in intersection)
    w_union = sum(idf.get(w, 1.0) for w in union)
    return w_intersection / w_union


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class _LRUTTLCache:
    """
    LRU cache with per-entry TTL. Not thread-safe — must be accessed under a lock.

    Stores (ids, inserted_at) pairs. Expired entries are lazily evicted on access;
    LRU entries are evicted when the cache reaches capacity.
    """

    def __init__(self, maxsize: int, ttl: float) -> None:
        self._maxsize = maxsize
        self._ttl = ttl
        self._store: OrderedDict[str, Tuple[List[str], float]] = OrderedDict()

    def get(self, key: str) -> Tuple[Optional[List[str]], float]:
        """Return (ids, inserted_at), or (None, 0.0) if absent or expired."""
        item = self._store.get(key)
        if item is None:
            return None, 0.0
        ids, ts = item
        if time.monotonic() - ts > self._ttl:
            del self._store[key]
            return None, 0.0
        self._store.move_to_end(key)
        return ids, ts

    def set(self, key: str, ids: List[str]) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (ids, time.monotonic())
        if len(self._store) > self._maxsize:
            self._store.popitem(last=False)  # evict least recently used

    def pop(self, key: str) -> None:
        self._store.pop(key, None)


class _SourceFeatures(NamedTuple):
    """Extracted scoring features for the source novel."""

    id: str
    domain: str
    words: Set[str]
    tags: Set[str]
    authors: Set[str]
    idf: Dict[str, float]  # IDF weight for each title word (precomputed, reused per candidate)


class _CandidateRow(NamedTuple):
    """A single row from the candidate fetch queries — matches _SCORE_COLS order."""

    id: str
    tags: List[str]
    domain: str
    title: str
    authors: Optional[str]


# ---------------------------------------------------------------------------
# Inverted index
# ---------------------------------------------------------------------------


class _InvertedIndex:
    """
    In-memory inverted index over novel titles.

    Replaces ILIKE queries for candidate selection, giving uniform performance
    across SQLite, PostgreSQL, and MySQL. Also provides IDF weights so that
    rare title words contribute more to the similarity score.
    """

    def __init__(self) -> None:
        self._word_ids: Dict[str, Set[str]] = {}  # word → set of novel IDs
        self._total: int = 0
        self._lock = threading.Lock()  # guards write operations only

    def build(self) -> None:
        """Load all (id, title) pairs from the DB and build the index."""
        with ctx.db.session() as sess:
            rows = sess.exec(sq.select(Novel.id, Novel.title)).all()
        word_ids: Dict[str, Set[str]] = {}
        for nid, title in rows:
            for w in _words(title):
                word_ids.setdefault(w, set()).add(nid)
        with self._lock:
            self._word_ids = word_ids
            self._total = len(rows)

    def add(self, novel_id: str, title: str) -> None:
        with self._lock:
            for w in _words(title):
                self._word_ids.setdefault(w, set()).add(novel_id)
            self._total += 1

    def remove(self, novel_id: str, title: str) -> None:
        with self._lock:
            for w in _words(title):
                ids = self._word_ids.get(w)
                if ids:
                    ids.discard(novel_id)
                    if not ids:
                        del self._word_ids[w]
            self._total = max(0, self._total - 1)

    def idf(self, word: str) -> float:
        """Smoothed IDF = log((N+1) / (df+1))."""
        df = len(self._word_ids.get(word, set()))
        return math.log((self._total + 1) / (df + 1)) if self._total > 0 else 1.0

    def candidates(self, words: Set[str], exclude_id: str, limit: int) -> List[str]:
        """
        Return up to `limit` candidate IDs sorted by number of matching title words
        (most overlapping words first, so the most relevant candidates are in the DB query).
        """
        counts: Counter = Counter()
        for w in words:
            for nid in self._word_ids.get(w, set()):
                counts[nid] += 1
        counts.pop(exclude_id, None)
        return [nid for nid, _ in counts.most_common(limit)]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
class RecommendationService:
    def __init__(self) -> None:
        self._index = _InvertedIndex()
        self._index_ready = False
        self._index_init_lock = threading.Lock()
        # Cache stores ranked novel IDs only — full Novel objects are never cached.
        self._cache: _LRUTTLCache = _LRUTTLCache(maxsize=CACHE_MAX_ENTRIES, ttl=CACHE_TTL_SECONDS)
        self._pending: Set[str] = set()  # novel IDs being refreshed in a background thread
        self._computing: Dict[str, threading.Event] = {}  # synchronous computes in progress
        self._cache_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Index lifecycle
    # ------------------------------------------------------------------

    def _ensure_index(self) -> None:
        """Lazy double-checked init: build the inverted index on first use."""
        if self._index_ready:
            return
        with self._index_init_lock:
            if self._index_ready:
                return
            self._index.build()
            self._index_ready = True

    def index_add(self, novel_id: str, title: str) -> None:
        """Call when a novel is persisted so it appears in future title candidates."""
        if self._index_ready:
            self._index.add(novel_id, title)

    def index_remove(self, novel_id: str, title: str) -> None:
        """Call when a novel is deleted to keep the inverted index consistent."""
        if self._index_ready:
            self._index.remove(novel_id, title)

    # ------------------------------------------------------------------
    # Core computation
    # ------------------------------------------------------------------

    def _load_novels(self, ids: List[str]) -> List[Novel]:
        """Fetch full Novel objects for the given IDs, preserving rank order."""
        if not ids:
            return []
        with ctx.db.session() as sess:
            id_to_novel: Dict[str, Novel] = {
                n.id: n for n in sess.exec(sq.select(Novel).where(sq.col(Novel.id).in_(ids))).all()
            }
        return [id_to_novel[i] for i in ids if i in id_to_novel]

    def _extract_features(self, novel: Novel) -> _SourceFeatures:
        """Extract scoring features from the source novel. Pure Python — no DB access."""
        words = _words(novel.title)
        return _SourceFeatures(
            id=novel.id,
            domain=novel.domain,
            words=words,
            tags={t.lower() for t in (novel.tags or [])},
            authors=_author_set(novel.authors),
            idf={w: self._index.idf(w) for w in words},
        )

    def _fetch_candidates(self, src: _SourceFeatures, sess: Any) -> List[_CandidateRow]:
        """Run the three-phase candidate query and return typed rows."""
        # Phase 1: inverted index lookup (cross-DB; no ILIKE full-table scan).
        # Candidates are pre-sorted by number of matching title words.
        sig_words = {w for w in src.words if len(w) >= MIN_WORD_LENGTH}
        title_ids = self._index.candidates(sig_words, src.id, TITLE_CANDIDATE_LIMIT)
        title_rows: List[_CandidateRow] = []
        if title_ids:
            title_rows = [
                _CandidateRow(*r)
                for r in sess.exec(
                    sq.select(*_SCORE_COLS).where(sq.col(Novel.id).in_(title_ids))  # type: ignore[call-overload]
                ).all()
            ]
        seen_ids = {r.id for r in title_rows}

        # Phase 2: same domain (domain column is indexed)
        domain_conds: List[Any] = [Novel.id != src.id, Novel.domain == src.domain]
        if seen_ids:
            domain_conds.append(sq.col(Novel.id).not_in(list(seen_ids)))
        domain_rows = [
            _CandidateRow(*r)
            for r in sess.exec(
                sq.select(*_SCORE_COLS).where(*domain_conds).limit(PHASE2_DOMAIN_LIMIT)  # type: ignore[call-overload]
            ).all()
        ]
        seen_ids.update(r.id for r in domain_rows)

        all_rows = title_rows + domain_rows

        # Phase 3: fallback when pool is still too small
        if len(all_rows) < CACHE_RESULTS:
            fb_conds: List[Any] = [Novel.id != src.id]
            if seen_ids:
                fb_conds.append(sq.col(Novel.id).not_in(list(seen_ids)))
            all_rows += [
                _CandidateRow(*r)
                for r in sess.exec(
                    sq.select(*_SCORE_COLS)  # type: ignore[call-overload]
                    .where(*fb_conds)
                    .limit(CACHE_RESULTS - len(all_rows))
                ).all()
            ]

        return all_rows

    def _score_candidates(self, src: _SourceFeatures, candidates: List[_CandidateRow]) -> List[str]:
        """Score candidates against the source novel. Pure CPU — no DB or index access."""
        scored: List[Tuple[float, str]] = []
        for row in candidates:
            cand_words = _words(row.title)
            cand_tags = {t.lower() for t in (row.tags or [])}
            cand_authors = _author_set(row.authors)

            # Extend the precomputed IDF dict with words exclusive to the candidate title.
            idf = {**src.idf, **{w: self._index.idf(w) for w in cand_words - src.words}}

            title_score = _idf_jaccard(src.words, cand_words, idf) ** 2 * WEIGHT_TITLE
            tag_score = _jaccard(src.tags, cand_tags) * WEIGHT_TAGS
            domain_score = float(WEIGHT_DOMAIN) if row.domain == src.domain else 0.0
            author_score = float(WEIGHT_AUTHOR) if src.authors & cand_authors else 0.0
            match_pct = title_score + tag_score + domain_score + author_score
            if match_pct > 0:
                scored.append((match_pct, row.id))

        return [rid for _, rid in heapq.nlargest(CACHE_RESULTS, scored, key=lambda x: x[0])]

    def _compute(self, novel_id: str) -> List[str]:
        """Orchestrate feature extraction, candidate fetch, and scoring."""
        self._ensure_index()
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel
            src = self._extract_features(novel)
            candidates = self._fetch_candidates(src, sess)
        return self._score_candidates(src, candidates)

    def _warmup(self, limit: int) -> None:
        start_time = time.monotonic()
        logger.info("Warmup started")
        with ctx.db.session() as sess:
            ids = sess.exec(
                sq.select(Novel.id).order_by(sq.desc(Novel.updated_at)).limit(limit)
            ).all()
        for novel_id in ids:
            try:
                self.get(novel_id)
            except Exception:
                pass
        logger.info(f"Warmup complete in {time.monotonic() - start_time:0.3} seconds")

    # ------------------------------------------------------------------
    # Stale-while-revalidate cache
    # ------------------------------------------------------------------

    def _refresh_background(self, novel_id: str) -> None:
        """Recompute recommendations in a background thread; always clears _pending."""
        try:
            top_ids = self._compute(novel_id)
            with self._cache_lock:
                self._cache.set(novel_id, top_ids)
        except Exception:
            pass
        finally:
            with self._cache_lock:
                self._pending.discard(novel_id)

    def _maybe_refresh(self, novel_id: str) -> None:
        """Spawn a background refresh thread if one is not already running."""
        with self._cache_lock:
            if novel_id in self._pending:
                return
            self._pending.add(novel_id)
        threading.Thread(target=self._refresh_background, args=(novel_id,), daemon=True).start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def warmup(self, limit: int = 100) -> None:
        threading.Thread(target=self._warmup, args=[limit], daemon=True).start()

    def invalidate(self, novel_id: str) -> None:
        with self._cache_lock:
            self._cache.pop(novel_id)

    def get(self, novel_id: str, limit: int = 8) -> List[Novel]:
        """
        Return novels ranked by similarity.

        Cache hit (fresh, age < FRESH_TTL_SECONDS):  return immediately.
        Cache hit (stale, age ≥ FRESH_TTL_SECONDS):  return immediately + background refresh.
        Cache miss, first thread:                     compute synchronously, store, return.
        Cache miss, concurrent thread:                wait for the first thread, then read cache.
        """
        while True:
            stale = False
            waiting: Optional[threading.Event] = None
            with self._cache_lock:
                cached, cached_time = self._cache.get(novel_id)
                if cached is not None:
                    stale = time.monotonic() - cached_time > FRESH_TTL_SECONDS
                elif novel_id not in self._computing:
                    # This thread will compute — register an event others can wait on.
                    compute_event = threading.Event()
                    self._computing[novel_id] = compute_event
                    break
                else:
                    waiting = self._computing[novel_id]

            if cached is not None:
                if stale:
                    self._maybe_refresh(novel_id)  # called outside lock — no deadlock
                return self._load_novels(cached[:limit])

            # Another thread is already computing this novel; wait for it then re-check cache.
            if waiting is not None:
                waiting.wait(timeout=60)

        try:
            top_ids = self._compute(novel_id)
            with self._cache_lock:
                self._cache.set(novel_id, top_ids)
            return self._load_novels(top_ids[:limit])
        finally:
            with self._cache_lock:
                self._computing.pop(novel_id, None)
            compute_event.set()
