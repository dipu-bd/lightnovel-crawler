# -*- coding: utf-8 -*-
"""A last-resort crawler for novel-shaped sites that have no source of their own.

Measured over a corpus of saved pages, chapter *bodies* need no site knowledge — a body
is reliably the densest run of prose on its page — while chapter *lists* are the hard
part, because navigation, sidebars, tag clouds and theme pickers are all sets of uniform
sibling links too. So the list detector scores containers rather than links, and every
answer carries a completeness verdict.

Returning twenty chapters of fifty-seven is the characteristic failure here, and it looks
exactly like success. Nothing below is allowed to report a number without also reporting
what it could not account for.
"""

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin, urlsplit

from ..core import Chapter, Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)

DIGITS = re.compile(r"\d+")
NAV_WORDS = re.compile(
    r"^(home|search|login|log ?in|sign ?up|register|privacy|terms|contact|about|dmca|"
    r"skip to content|menu|next|previous|prev|back|top|read|read now|start reading|"
    r"view|view all|more|share|report|bookmark|download|comments?|report error|"
    r"advertisement|continue reading|first chapter|last chapter|latest chapter)$",
    re.I,
)
NAV_CONTAINER = re.compile(r"nav|menu|sidebar|footer|header|breadcrumb|widget|banner|promo", re.I)
MORE_CONTROL = re.compile(r"show\s+\d+\s+more|show\s+more|load\s+more|see\s+all|view\s+all", re.I)
LIST_HINT = re.compile(r"chapter|episode|volume|toc|content", re.I)
# Taxonomy links are the most convincing impostor: dozens of uniform sibling anchors with
# tidy titles. Without this, genre pills get returned as the chapter list.
TAXONOMY = re.compile(
    r"/(genres?|tags?|categor(y|ies)|authors?|artists?|search|browse|library|"
    r"users?|u|profile|status|rank(ing)?s?|latest|popular|new)(/|$|\?)",
    re.I,
)


def _shape(path: str) -> str:
    return DIGITS.sub("#", path)


def _last_number(text: str) -> Optional[int]:
    found = DIGITS.findall(text or "")
    return int(found[-1]) if found else None


def _first_number(text: str) -> Optional[int]:
    match = DIGITS.search(text or "")
    return int(match.group()) if match else None


@dataclass
class _Candidate:
    anchors: List[Any] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    key: str = ""
    score: float = 0.0
    why: str = ""


@dataclass
class GenericVerdict:
    """What was found, and what could not be accounted for."""

    chapters: List[Tuple[str, str]]
    complete: bool
    notes: List[str]
    confidence: str
    ordering: str

    def summary(self) -> str:
        head = f"{len(self.chapters)} chapters, {self.confidence} confidence, by {self.ordering}"
        return head + ("" if self.complete else "; " + "; ".join(self.notes))


class GenericCrawler(SoupTemplate):
    """Guesses a site's structure. Never registered as a source — built on demand."""

    base_url: Any = []

    # Nothing is known about this host, so pace as an unfamiliar visitor rather than at
    # the default a written source is allowed to assume it has earned.
    request_rate_limit = 1

    # Below this the winner is only the best of a bad field. Margin alone cannot see
    # that: the best of two equally hopeless groups still beats the other comfortably.
    weak_score = 1.5
    min_chapters = 2

    # Rendering is a guess about a guess here, so it gets a short leash.
    render_timeout = 45

    def __init__(self, parser=None, origin=None, *, scraper=None) -> None:
        if origin:
            self.base_url = [origin]
        super().__init__(parser=parser, origin=origin, scraper=scraper)
        self.verdict: Optional[GenericVerdict] = None

    # ------------------------------------------------------------------ novel

    def read_novel(self, novel: Novel) -> None:
        soup = self.scraper.get_soup(self.absolute_url(novel.url))
        verdict = self._chapters(soup, novel.url)

        if len(verdict.chapters) < self.min_chapters and self._can_render():
            rendered = self._render(novel.url)
            if rendered is not None:
                found = self._chapters(rendered, novel.url)
                if len(found.chapters) >= len(verdict.chapters):
                    soup, verdict = rendered, found

        self._metadata(soup, novel)
        for title, url in verdict.chapters:
            novel.add_chapter(title=title, url=url)

        self.verdict = verdict
        novel.generic_verdict = verdict.summary()
        if not verdict.chapters:
            logger.warning("Generic crawler found no chapter list on %s", novel.url)
        else:
            logger.warning(
                "Generic crawler (no source for this site) — %s. Treat the result as "
                "unverified: %s",
                verdict.summary(),
                novel.url,
            )

    def _can_render(self) -> bool:
        return bool(getattr(self.scraper, "render_soup", None))

    def _render(self, url: str) -> Optional[PageSoup]:
        # A shell's own navigation satisfies `a[href]` immediately, so waiting on that
        # returns the same empty page it started with — hence a chapter-shaped condition.
        #
        # Bounded on purpose. This runs against hosts nothing is known about, where a
        # wrong guess costs the whole render budget and the site may be challenged on top
        # of that; three unbounded attempts is several minutes before anything is read.
        for wait in ("a[href*='chapter']", "main a[href]"):
            try:
                return self.scraper.render_soup(
                    self.absolute_url(url), wait_for=wait, timeout=self.render_timeout
                )
            except Exception:
                continue
        return None

    def _metadata(self, soup: PageSoup, novel: Novel) -> None:
        def meta(*names: str) -> str:
            for name in names:
                tag = soup.select_one(f'meta[property="{name}"], meta[name="{name}"]')
                if tag:
                    value = str(tag.get("content") or "").strip()
                    if value:
                        return value
            return ""

        novel.title = meta("og:title", "title")
        if not novel.title:
            heading = soup.select_one("h1")
            novel.title = heading.get_text(" ", strip=True) if heading else ""

        cover = meta("og:image", "image")
        if cover:
            novel.cover_url = self.absolute_url(cover)

        synopsis = meta("og:description", "description")
        if synopsis:
            novel.synopsis = f"<p>{synopsis}</p>"

        link = soup.select_one("a[href*='/author/'], a[href*='/authors/'], a[rel=author]")
        if link:
            text = link.get_text(" ", strip=True)
            if text and len(text) < 80:
                novel.author = text
        if not novel.author:
            novel.author = meta("og:author", "author")

    # --------------------------------------------------------------- chapters

    def _chapters(self, soup: PageSoup, novel_url: str) -> GenericVerdict:
        base = self._strip(self.absolute_url(novel_url))
        host = urlsplit(base).netloc
        groups = self._group(soup, base, host)
        if not groups:
            return GenericVerdict([], False, ["no chapter-shaped links here"], "low", "document")

        best = max(groups, key=lambda c: c.score)
        chapters, ordering = self._order(best)
        notes, complete = self._completeness(soup, chapters)
        return GenericVerdict(
            chapters, complete, notes, self._confidence(best, chapters, complete, groups), ordering
        )

    def _strip(self, url: str) -> str:
        split = urlsplit(url)
        return f"{split.scheme}://{split.netloc}{split.path}".rstrip("/")

    def _group(self, soup: PageSoup, base: str, host: str) -> List[_Candidate]:
        buckets: Dict[str, _Candidate] = {}
        for anchor in soup.select("a[href]"):
            raw = str(anchor.get("href") or "")
            # A bare fragment or a pure query resolves onto the novel's own path, which
            # is how "Skip to content" and share buttons arrive looking like chapter one.
            if not raw or raw.startswith("#") or raw.startswith("javascript:"):
                continue
            url = urljoin(base + "/", raw)
            split = urlsplit(url)
            if split.scheme not in ("http", "https") or split.netloc != host:
                continue
            clean = self._strip(url)
            if clean == base:
                continue
            title = anchor.get_text(" ", strip=True)
            if not title or NAV_WORDS.match(re.sub(r"[^a-z ]", "", title.lower()).strip()):
                continue
            # Group on markup, not on the URL: masking digits does not collapse
            # `chapter-1-wow-...` and `chapter-2-if-...`, so a URL key gives every chapter
            # its own group and the real list never forms. Split on the novel prefix too,
            # because a theme that prints the whole site's page tree renders this novel's
            # chapters and every other novel in one list with identical markup.
            inside = "in" if clean.startswith(base + "/") else "out"
            key = f"{self._signature(anchor)}|{inside}"
            bucket = buckets.setdefault(key, _Candidate(key=key))
            bucket.anchors.append(anchor)
            bucket.urls.append(url)
            bucket.titles.append(title)

        out: List[_Candidate] = []
        # Counting an ancestor's anchors is a full subtree scan and groups share
        # ancestors constantly, so without this the page is re-walked per group.
        counts: Dict[int, int] = {}
        for bucket in sorted(buckets.values(), key=lambda b: -len(b.urls))[:60]:
            if len(bucket.urls) < self.min_chapters:
                continue
            bucket.score, bucket.why = self._score(bucket, base, counts)
            out.append(bucket)
        return out

    def _signature(self, anchor, depth: int = 3) -> str:
        parts = []
        node = anchor
        for _ in range(depth + 1):
            if node is None or not hasattr(node, "get"):
                break
            classes = node.get("class") or []
            parts.append(f"{getattr(node, 'name', '?')}.{classes[0] if classes else ''}")
            node = node.parent
        return "|".join(parts)

    def _score(self, cand: _Candidate, base: str, counts: Dict[int, int]) -> Tuple[float, str]:
        reasons: List[str] = []
        size = len(cand.urls)
        # Square-rooted: a bigger list should win, but not so decisively that a 65-entry
        # sidebar of other novels outranks a real three-chapter list on every signal.
        score = size**0.5

        ancestor = self._ancestor(cand.anchors)
        if ancestor is not None:
            key = id(ancestor)
            if key not in counts:
                counts[key] = len(ancestor.select("a[href]"))
            total = counts[key] or size
            tightness = size / total
            score *= 0.25 + 0.75 * tightness
            reasons.append(f"tightness={tightness:.2f}")
            if self._in_navigation(ancestor):
                score *= 0.15
                reasons.append("inside navigation")
            if LIST_HINT.search(" ".join(self._context(ancestor))):
                score *= 1.4
                reasons.append("container names a chapter list")

        paths = [urlsplit(u).path for u in cand.urls]
        if len({_shape(p) for p in paths}) <= max(2, size // 10) and any(
            DIGITS.search(p) for p in paths
        ):
            score *= 1.5
            reasons.append("numbered url shape")

        if sum(bool(TAXONOMY.search(p)) for p in paths) > size * 0.5:
            score *= 0.08
            reasons.append("taxonomy links")

        # Chapters live under the novel, or else carry an id identifying them. Requiring
        # the prefix alone is wrong — plenty of sites route chapters outside the novel's
        # path — but a group that is neither under it nor numbered is a list of other
        # things: sibling novels, a page tree, a tag cloud.
        under = sum(u.startswith(base + "/") for u in cand.urls)
        numbered = sum(bool(DIGITS.search(p)) for p in paths)
        if under > size * 0.8:
            score *= 1.3
            reasons.append("under the novel path")
        elif numbered < size * 0.5:
            depth = base.count("/")
            same_depth = sum(self._strip(u).count("/") == depth for u in cand.urls)
            score *= 0.03 if same_depth > size * 0.8 else 0.12
            reasons.append("neither under the novel nor numbered")

        if sum(bool(LIST_HINT.search(p)) for p in paths) > size * 0.6:
            score *= 1.3
            reasons.append("chapter-ish paths")

        unique = len(set(cand.titles)) / size
        score *= 0.4 + 0.6 * unique
        reasons.append(f"unique-titles={unique:.2f}")
        return score, ", ".join(reasons)

    def _context(self, tag) -> List[str]:
        out: List[str] = []
        node = tag
        for _ in range(3):
            if node is None or not hasattr(node, "get"):
                break
            out.extend(str(x) for x in (node.get("class") or []))
            out.append(str(node.get("id") or ""))
            out.append(str(getattr(node, "name", "") or ""))
            node = node.parent
        return out

    def _in_navigation(self, tag) -> bool:
        node = tag
        for _ in range(4):
            if node is None or not hasattr(node, "get"):
                break
            if getattr(node, "name", "") in ("nav", "aside", "footer", "header"):
                return True
            blob = " ".join(str(x) for x in (node.get("class") or []))
            blob += " " + str(node.get("id") or "")
            if NAV_CONTAINER.search(blob):
                return True
            node = node.parent
        return False

    def _ancestor(self, anchors: List[Any]) -> Any:
        if not anchors:
            return None
        chains = []
        for anchor in anchors[:40]:
            chain = []
            node = anchor
            while node is not None:
                chain.append(node)
                node = getattr(node, "parent", None)
            chains.append(list(reversed(chain)))
        shortest = min(len(c) for c in chains)
        found = None
        for depth in range(shortest):
            if len({id(c[depth]) for c in chains}) != 1:
                break
            found = chains[0][depth]
        return found

    def _order(self, cand: _Candidate) -> Tuple[List[Tuple[str, str]], str]:
        pairs = list(zip(cand.titles, cand.urls))
        for label, maybe in (
            ("href-number", [_last_number(urlsplit(u).path) for u in cand.urls]),
            ("title-number", [_first_number(t) for t in cand.titles]),
        ):
            if any(n is None for n in maybe) or len(set(maybe)) != len(maybe):
                continue
            numbers = [n for n in maybe if n is not None]
            return [p for _, p in sorted(zip(numbers, pairs), key=lambda x: x[0])], label

        numbers = [_first_number(t) for t in cand.titles]
        known = [n for n in numbers if n is not None]
        if len(known) >= 3 and known == sorted(known, reverse=True):
            return list(reversed(pairs)), "document (reversed)"
        return pairs, "document"

    def _completeness(self, soup: PageSoup, chapters) -> Tuple[List[str], bool]:
        notes: List[str] = []
        complete = True

        maybe = [_last_number(urlsplit(u).path) for _, u in chapters]
        if maybe and all(n is not None for n in maybe):
            numbers = [n for n in maybe if n is not None]
            highest = max(numbers)
            if highest > len(numbers):
                notes.append(f"numbers reach {highest} but only {len(numbers)} links were found")
                complete = False
            ordered = sorted(numbers)
            if any(b - a > 1 for a, b in zip(ordered, ordered[1:])):
                complete = False
                notes.append("the numbering has gaps")

        control = MORE_CONTROL.search(soup.get_text(" ", strip=True))
        if control:
            notes.append(f"the page offers {control.group(0)!r} — the list is likely truncated")
            complete = False

        if soup.select("a[href*='page='], a[href*='/page/'], .pagination a, .pager a"):
            notes.append("the list is paginated and later pages were not followed")
            complete = False
        return notes, complete

    def _confidence(self, best: _Candidate, chapters, complete: bool, groups) -> str:
        if not chapters:
            return "low"
        rivals = sorted((c.score for c in groups), reverse=True)
        margin = (rivals[0] / rivals[1]) if len(rivals) > 1 and rivals[1] else 99.0
        penalised = any(
            phrase in best.why for phrase in ("inside navigation", "neither under", "taxonomy")
        )
        if best.score < self.weak_score or penalised:
            return "low"
        if complete and margin > 2 and len(chapters) >= 5:
            return "high"
        return "medium" if margin > 1.3 else "low"

    # ------------------------------------------------------------------- body

    def select_chapter_tags(self, tag: PageSoup, novel: Novel, volume=None) -> Iterable[PageSoup]:
        return []

    def download_chapter(self, chapter: Chapter) -> None:
        url = self.build_chapter_url(chapter)
        soup = self.scraper.get_soup(url)
        body = self.find_body(soup)
        if body is None and self._can_render():
            for wait in ("article p", "main p"):
                try:
                    soup = self.scraper.render_soup(url, wait_for=wait, timeout=self.render_timeout)
                except Exception:
                    continue
                body = self.find_body(soup)
                if body is not None:
                    break
        if body is None:
            logger.warning("Generic crawler found no chapter text at %s", url)
            return
        self.parse_chapter_body(body, chapter)

    def find_body(self, soup: PageSoup) -> Any:
        """The densest run of prose on the page.

        Shortlisted on direct ``<p>`` children first: scoring every container instead
        means a ``get_text`` over the whole subtree for each of several thousand tags,
        which is quadratic and takes minutes on a large chapter page.
        """
        shortlist: List[Tuple[Any, int]] = []
        for tag in soup.find_all(["div", "article", "section", "main", "td"]):
            paragraphs = tag.find_all("p", recursive=False)
            if len(paragraphs) >= 3:
                shortlist.append((tag, len(paragraphs)))
        if not shortlist:
            for tag in soup.find_all(["div", "article", "section", "td"]):
                if len(tag.find_all("br", recursive=False)) >= 5:
                    shortlist.append((tag, 0))

        best, best_score = None, 0.0
        for tag, paragraphs in shortlist:
            if self._in_navigation(tag):
                continue
            text = tag.get_text(" ", strip=True)
            if len(text) < 400:
                continue
            links = sum(len(a.get_text(" ", strip=True)) for a in tag.select("a[href]"))
            density = links / max(len(text), 1)
            if density > 0.35:
                continue
            score = len(text) * (1 - density) * (1 + 0.15 * min(paragraphs, 20))
            if score > best_score:
                best, best_score = tag, score
        return best
