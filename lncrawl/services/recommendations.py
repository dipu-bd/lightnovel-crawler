from collections import OrderedDict
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
MIN_WORD_LENGTH = 2  # title words shorter than this are skipped in index lookups
MAX_DF_RATIO = 0.3  # words present in more titles than this fraction are near stop-words
MIN_DF_CAP = 100  # never treat a word as a stop-word below this document frequency

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


def _idf(total: int, df: int) -> float:
    """Smoothed IDF = log((N+1) / (df+1))."""
    return math.log((total + 1) / (df + 1)) if total > 0 else 1.0


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

    Tracks the indexed words per novel, so `add` is an upsert (a title change
    cleans up the old words) and `remove` needs only the novel ID.
    """

    def __init__(self) -> None:
        self._word_ids: Dict[str, Set[str]] = {}  # word → set of novel IDs
        self._novel_words: Dict[str, Set[str]] = {}  # novel ID → indexed title words
        self._lock = threading.Lock()  # guards reads and writes of both maps

    def build(self) -> None:
        """Load all (id, title) pairs from the DB and build the index."""
        with ctx.db.session() as sess:
            rows = sess.exec(sq.select(Novel.id, Novel.title)).all()
        word_ids: Dict[str, Set[str]] = {}
        novel_words: Dict[str, Set[str]] = {}
        for nid, title in rows:
            words = _words(title)
            novel_words[nid] = words
            for w in words:
                word_ids.setdefault(w, set()).add(nid)
        with self._lock:
            self._word_ids = word_ids
            self._novel_words = novel_words

    def _unlink(self, novel_id: str, words: Set[str]) -> None:
        for w in words:
            ids = self._word_ids.get(w)
            if ids:
                ids.discard(novel_id)
                if not ids:
                    del self._word_ids[w]

    def add(self, novel_id: str, title: str) -> None:
        """Insert a novel, or update its indexed words if the title changed."""
        new_words = _words(title)
        with self._lock:
            old_words = self._novel_words.get(novel_id, set())
            self._unlink(novel_id, old_words - new_words)
            for w in new_words - old_words:
                self._word_ids.setdefault(w, set()).add(novel_id)
            self._novel_words[novel_id] = new_words

    def remove(self, novel_id: str) -> None:
        with self._lock:
            old_words = self._novel_words.pop(novel_id, None)
            if old_words:
                self._unlink(novel_id, old_words)

    def idf(self, word: str) -> float:
        ids = self._word_ids.get(word)
        return _idf(len(self._novel_words), len(ids) if ids else 0)

    def candidates(self, words: Set[str], exclude_id: str, limit: int) -> List[str]:
        """
        Return up to `limit` candidate IDs ranked by IDF-weighted title-word overlap,
        so preselection mirrors the final title score. Near stop-words (present in
        more than MAX_DF_RATIO of all titles) are skipped — they carry almost no
        signal but match huge ID sets — unless every matched word is that common.
        """
        with self._lock:
            total = len(self._novel_words)
            df_cap = max(MIN_DF_CAP, MAX_DF_RATIO * total)
            matched = [ids for w in words if (ids := self._word_ids.get(w))]
            informative = [ids for ids in matched if len(ids) <= df_cap]
            scores: Dict[str, float] = {}
            for ids in informative or matched:
                weight = _idf(total, len(ids))
                for nid in ids:
                    scores[nid] = scores.get(nid, 0.0) + weight
        scores.pop(exclude_id, None)
        return heapq.nlargest(limit, scores, key=scores.__getitem__)


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

    def index_remove(self, novel_id: str) -> None:
        """Call when a novel is deleted to keep the inverted index consistent."""
        if self._index_ready:
            self._index.remove(novel_id)

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
        """Score candidates against the source novel. Pure CPU — no DB access."""
        # IDF lookups are memoized across all candidates — titles share many words.
        idf_cache: Dict[str, float] = dict(src.idf)
        src_idf_sum = sum(src.idf.values())

        scored: List[Tuple[float, str]] = []
        for row in candidates:
            # IDF-weighted Jaccard: intersection weight / union weight, in one pass.
            w_inter = 0.0
            w_extra = 0.0
            for w in _words(row.title):
                weight = idf_cache.get(w)
                if weight is None:
                    weight = self._index.idf(w)
                    idf_cache[w] = weight
                if w in src.words:
                    w_inter += weight
                else:
                    w_extra += weight
            w_union = src_idf_sum + w_extra
            title_sim = w_inter / w_union if w_union else 0.0

            score = title_sim**2 * WEIGHT_TITLE
            score += _jaccard(src.tags, {t.lower() for t in (row.tags or [])}) * WEIGHT_TAGS
            if row.domain == src.domain:
                score += WEIGHT_DOMAIN
            if src.authors and src.authors & _author_set(row.authors):
                score += WEIGHT_AUTHOR
            if score > 0:
                scored.append((score, row.id))

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
