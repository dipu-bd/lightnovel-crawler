import hashlib
import json
from typing import Any, Dict, List, Optional

import typer

from ...context import ctx
from ...core.models import Chapter, Novel


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


def _sample(total: int, count: int) -> List[int]:
    """Which chapter indices to fetch: first, last, and the middle ones between them.

    The middle matters. First and last alone would pass a body split across pages whose
    `join` is wrong, which is the failure the equivalence gate was written to catch.
    """
    if total <= 0 or count <= 0:
        return []
    if total <= count:
        return list(range(total))
    if count == 1:
        return [0]
    step = (total - 1) / (count - 1)
    return sorted({int(round(index * step)) for index in range(count)})


def shadow_dump(
    url: str = typer.Argument(help="A novel URL to read with whichever tier serves it."),
    chapters: int = typer.Option(3, "--chapters", "-c", help="How many chapter bodies to sample."),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Write here instead of stdout."
    ),
):
    """Read a novel with whichever tier serves its host and print it as JSON.

    This is the half of shadow-diff that has to live beside the crawler. The comparison
    itself belongs in the definitions repository, which can run this twice and diff the
    two documents; it cannot import this package, and this package must never import the
    interpreter's side either.

    Which tier answers is not an argument, because it is not this command's decision: the
    app resolves a host by precedence and that is exactly what a shadow diff needs to
    capture. Point `LNCRAWL_SPECS_PATH` at a directory with no `specs/` to get the legacy
    tier instead, and the `tier` field in the output records which one actually ran.

    The body is reported as a length and a digest rather than as text. Two tiers that
    differ by one whitespace character should be visible, but a diff report is not a place
    to paste a novel.
    """
    ctx.sources.load(sync_remote=False)
    ctx.sources.ensure_load()

    domain = ctx.sources.get_domain(url)
    source = ctx.sources.get_source(domain)
    crawler = ctx.sources.init_crawler(url)

    report: Dict[str, Any] = {
        "url": url,
        "domain": domain,
        "tier": source.tier,
        "crawler_id": source.crawler_id,
    }
    try:
        novel = Novel(url=url)
        crawler.read_novel(novel)
        crawler.format_novel(novel)

        report.update(
            title=novel.title,
            cover_url=novel.cover_url or "",
            authors=novel.author or "",
            synopsis_length=len(novel.synopsis or ""),
            synopsis_digest=_digest(novel.synopsis or ""),
            tags=sorted(novel.tags or []),
            language=novel.language,
            volumes=len(novel.volumes or []),
            chapter_count=len(novel.chapters or []),
            first_chapter=(novel.chapters[0].title if novel.chapters else ""),
            last_chapter=(novel.chapters[-1].title if novel.chapters else ""),
        )

        sampled = []
        for index in _sample(len(novel.chapters or []), chapters):
            chapter: Chapter = novel.chapters[index]
            try:
                crawler.download_chapter(chapter)
                crawler.format_chapter(chapter)
                body = chapter.body or ""
                sampled.append(
                    {
                        "index": index,
                        "title": chapter.title,
                        "url": chapter.url,
                        "length": len(body),
                        "digest": _digest(body),
                    }
                )
            except Exception as error:
                sampled.append({"index": index, "url": chapter.url, "error": repr(error)[:200]})
        report["sampled"] = sampled
    except Exception as error:
        report["error"] = repr(error)[:300]
    finally:
        crawler.close()

    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if output:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
