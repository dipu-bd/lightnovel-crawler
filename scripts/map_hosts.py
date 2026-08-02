#!/usr/bin/env python3
"""
Find a usable novel page URL for each host, and record what it implies about the site.

Working the source-request backlog, the step that fails most often is not writing a parser
— it is finding one novel URL to point a parser at. Guessing from a word list does not
survive contact with the corpus: `/truyen/`, `/ranobe/`, `/obra/`, `/book/1067.html` and
bare slugs are all novel pages, and an English regex misses every one of them.

This looks for the shape instead. On a listing page the novel links are whichever path shape
repeats most, with digits collapsed so `/book/1067.html` and `/book/1068.html` count as one
shape. Chapters are then found by containment — a chapter lives underneath its novel's URL —
which needs no vocabulary at all.

Output is `scripts/research/novel-urls.json`, consumed by nothing at runtime. It exists so
the next person can test a template against a host without re-deriving where its novels are:

    uv run python scripts/map_hosts.py --hosts example.com,other.net
    uv run python scripts/map_hosts.py --from-index --limit 50
    uv run python scripts/map_hosts.py --hosts-file hosts.json --proxy socks5h://127.0.0.1:9250

Prefer `--proxy` over a direct run. An ISP that answers blocked domains with its own page
returns a `200` rather than an error, so a direct survey reports a live site as redirected
to somewhere unrelated — which reads as a dead domain and is the one mistake this corpus
must not make.

Results append as they complete, so a long run can be watched and a kill keeps the work
already done.

No browser is used, deliberately. Firefox caps concurrent WebDriver-BiDi sessions and
reports the excess as "the browser exited immediately", which is indistinguishable from a
site refusing the request — running solvers wide produces confident wrong answers. A host
behind a managed challenge therefore comes back `unreachable` here; map those one at a time
through the app's own scraper instead.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys
from threading import Lock
from typing import Any, Dict, List, Optional

import typer

workdir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(workdir))

from lncrawl.context import ctx  # noqa: E402

app = typer.Typer(help="Map hosts to a confirmed novel URL by analysing link shapes.")

DEFAULT_OUT = workdir / "scripts" / "research" / "novel-urls.json"

# Segments that start a listing, a policy page or an asset path rather than a novel.
SKIP_SEG = re.compile(
    r"^(tag|tags|genre|genres|category|categories|page|author|authors|user|users|login|"
    r"register|search|css|js|static|assets|images|img|feed|rss|wp-|api|cdn|privacy|contact|"
    r"about|terms|dmca|sitemap|policy|faq|donate|discord)",
    re.I,
)
API_HINT = re.compile(
    r"[\"'](https?://[a-z0-9.-]*api[a-z0-9.-]*\.[a-z]{2,})|[\"'](/api/[a-z0-9/_-]{2,36})[\"']"
)

_lock = Lock()
_state: Dict[str, Any] = {"done": 0, "total": 0, "handle": None, "proxy": ""}


def path_shape(path: str) -> str:
    """Collapse a path to its shape: digits become N, the last segment becomes *."""
    segs = [s for s in path.split("/") if s]
    return "/".join(
        "N" if re.fullmatch(r"\d+", s) else ("*" if i == len(segs) - 1 else s)
        for i, s in enumerate(segs)
    )


def local_paths(soup: Any, host: str) -> List[str]:
    bare = host.removeprefix("www.")
    out = []
    for anchor in soup.select("a[href]"):
        href = str(anchor.get("href") or "").split("#")[0].split("?")[0]
        if href.startswith("http") and bare not in href:
            continue
        path = re.sub(r"^https?://[^/]+", "", href)
        if not path.startswith("/"):
            path = "/" + path
        out.append(path)
    return out


def pick_novel_path(paths: List[str]) -> Optional[str]:
    """The novel listing is the repeating shape with the most distinct members."""
    by_shape: Dict[str, set] = defaultdict(set)
    for path in paths:
        segs = [s for s in path.split("/") if s]
        if not segs or len(segs) > 3 or SKIP_SEG.match(segs[0]):
            continue
        by_shape[path_shape(path)].add(path)
    for _, members in sorted(by_shape.items(), key=lambda kv: -len(kv[1])):
        if len(members) >= 4:
            return sorted(members)[0]
    return None


def probe(host: str) -> Dict[str, Any]:
    from scraper import ExitKind, ExitSpec, Scraper, ScraperConfig

    row: Dict[str, Any] = {"host": host}
    # Survey timeouts on purpose: with the library defaults a host that accepts a
    # connection and then goes silent costs about eleven minutes of retries, which is
    # enough to make a few hundred hosts look like a hang.
    settings: Dict[str, Any] = dict(raise_for_status=False, timeout=(10, 30), max_attempts=2)
    proxy = _state.get("proxy")
    if proxy:
        settings["exits"] = [ExitSpec(url=proxy, kind=ExitKind.TOR, label="survey")]
    scraper = Scraper(f"https://{host}/", ScraperConfig(**settings))
    try:
        home = scraper.get(f"https://{host}/")
    except Exception as exc:  # noqa: BLE001
        row["verdict"] = "unreachable"
        row["detail"] = type(exc).__name__
        return finish(row)

    text = home.text or ""
    row["api_hints"] = sorted({m[0] or m[1] for m in API_HINT.findall(text)})[:4]

    soup = scraper.make_soup(text)
    paths = local_paths(soup, host)
    row["shapes"] = Counter(path_shape(p) for p in paths).most_common(4)

    novel_path = pick_novel_path(paths)
    if not novel_path:
        row["verdict"] = "no-novel-shape"
        return finish(row)

    row["novel_url"] = f"https://{host}{novel_path}"
    try:
        page = scraper.get_soup(row["novel_url"])
    except Exception as exc:  # noqa: BLE001
        row["verdict"] = "novel-fetch-failed"
        row["detail"] = type(exc).__name__
        return finish(row)

    row["h1"] = [(e.text or "").strip()[:60] for e in page.select("h1")][:2]

    # A chapter sits underneath its novel's own path. Language-independent, unlike
    # matching the word "chapter" — twkan and shubaow number theirs.
    stem = re.sub(r"\.html?$", "", novel_path.rstrip("/"))
    hrefs = sorted({str(a.get("href")) for a in page.select("a[href]")})
    chapters = [
        h for h in hrefs if stem and stem in h and h.rstrip("/").removesuffix(".html") != stem
    ]
    row["chapter_links"] = len(chapters)
    row["chapter_sample"] = chapters[:2]
    row["verdict"] = "mapped" if chapters else "no-chapters-on-novel-page"
    return finish(row)


def finish(row: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        _state["done"] += 1
        flag = "MAPPED" if row.get("verdict") == "mapped" else "      "
        typer.echo(
            f"[{_state['done']:>4}/{_state['total']}] {flag} {row['host']:<34} "
            f"{row.get('verdict')} {row.get('chapter_links', '')}",
            err=True,
        )
        handle = _state["handle"]
        if handle:
            handle.write(json.dumps(row) + "\n")
            handle.flush()
    return row


def index_hosts() -> List[str]:
    ctx.setup()
    return sorted({str(info.domain) for info in ctx.sources.list()})


@app.command()
def main(
    hosts: str = typer.Option("", help="Comma-separated hosts to map."),
    hosts_file: Path = typer.Option(None, help="JSON file holding a list of hosts."),
    from_index: bool = typer.Option(False, help="Map every host already in the source index."),
    limit: int = typer.Option(0, help="Stop after this many hosts (0 = no limit)."),
    workers: int = typer.Option(
        16,
        help="Concurrent probes. Keep well below this if a browser solver is involved elsewhere.",
    ),
    out: Path = typer.Option(DEFAULT_OUT, help="Where to write the corpus."),
    jsonl: Path = typer.Option(None, help="Optional incremental JSONL log."),
    proxy: str = typer.Option(
        "",
        help="Send every probe through this proxy, e.g. socks5h://127.0.0.1:9250.",
    ),
) -> None:
    ctx.setup()
    _state["proxy"] = proxy

    targets: List[str] = []
    if hosts:
        targets += [h.strip() for h in hosts.split(",") if h.strip()]
    if hosts_file:
        targets += json.loads(Path(hosts_file).read_text())
    if from_index:
        targets += index_hosts()
    targets = [h for h in dict.fromkeys(targets) if h and "*" not in h]
    if limit:
        targets = targets[:limit]
    if not targets:
        raise typer.BadParameter("give --hosts, --hosts-file or --from-index")

    _state["total"] = len(targets)
    _state["handle"] = open(jsonl, "w", encoding="utf-8") if jsonl else None
    typer.echo(f"mapping {len(targets)} hosts with {workers} workers", err=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(probe, targets))
    if _state["handle"]:
        _state["handle"].close()

    existing: Dict[str, Any] = {}
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8")).get("hosts", {})
    for row in rows:
        if row.get("novel_url"):
            existing[row["host"]] = {
                key: row[key]
                for key in ("novel_url", "chapter_links", "chapter_sample", "shapes", "api_hints")
                if row.get(key)
            }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "_note": "A confirmed novel page URL per host, found by repeating-path-shape "
                "analysis rather than by an English path regex. Use these to test a "
                "template against a host without re-deriving where its novels live.",
                "hosts": dict(sorted(existing.items())),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    counts = Counter(r["verdict"] for r in rows)
    typer.echo("", err=True)
    for verdict, count in counts.most_common():
        typer.echo(f"  {verdict:<26} {count}", err=True)
    typer.echo(f"\n{out} now holds {len(existing)} hosts", err=True)
    for row in rows:
        if row.get("verdict") == "mapped":
            typer.echo(row["novel_url"])


if __name__ == "__main__":
    app()
