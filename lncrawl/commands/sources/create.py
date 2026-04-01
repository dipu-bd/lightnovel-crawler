import logging
import re
from enum import Enum
from typing import List, Optional

import questionary
import typer
from openai import OpenAI
from rich import print

from ...assets.languages import language_codes
from ...context import ctx
from ...utils.url_tools import extract_base, extract_host, validate_url
from .app import app

logger = logging.getLogger(__name__)


class Feature(str, Enum):
    has_manga = "manga"
    has_mtl = "mtl"
    can_search = "search"
    can_login = "login"
    has_volumes = "volumes"


@app.command("create", help="Create a source.")
def create_one(
    non_interactive: bool = typer.Option(
        False,
        "--noin",
        help="Disable interactive mode",
    ),
    locale: Optional[str] = typer.Option(
        None,
        "-l",
        "--locale",
        help="Content language (ISO 639-1 code)",
    ),
    features: Optional[List[Feature]] = typer.Option(
        None,
        "-f",
        "--features",
        help="Crawler features. e.g.: -f search -f mtl",
    ),
    use_openai: Optional[bool] = typer.Option(
        None,
        "--openai",
        is_flag=True,
        help="Use OpenAI model for auto generation",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        is_flag=True,
        help="Replace existing crawler with new one",
    ),
    url: str = typer.Argument(
        default=None,
        help="The URL of the source website.",
    ),
):
    # validate host
    host = extract_host(url)
    if not host:
        if non_interactive:
            print(f"[red]Invalid URL: {url}[/red]")
            return
        url = _prompt_url()
        host = extract_host(url)
        if not host:
            return

    # ensure locale
    if locale is None:
        locale = "" if non_interactive else _prompt_locale()

    # build crawler name and file_name
    name = " ".join(host.split(".")).title()
    name = re.sub(r"[^A-Za-z0-9]", "_", name)
    file_name = name.casefold()
    name = name.replace("_", "")
    name += "Crawler"

    # check file path
    file_path = _build_path(locale, file_name)
    if (
        file_path.is_file()
        and not overwrite
        and (non_interactive or not _prompt_replace(str(file_path)))
    ):
        print(f"[red]A file already exists for [b]{host}[/b]:[/red] [cyan]{file_path}[/cyan]")
        return

    # ensure capabilities
    if features is None:
        if non_interactive:
            features = []
        else:
            features = _prompt_features()

    # ensure to use openai
    if use_openai is None:
        if non_interactive:
            use_openai = bool(ctx.config.app.openai_key)
        else:
            use_openai = _prompt_use_openai()
    if use_openai and not ctx.config.app.openai_key:
        if non_interactive:
            use_openai = False
        else:
            ctx.config.app.openai_key = _prompt_openai_key()

    # generate content stub
    base_url = extract_base(url)
    content = _generate_stub(
        name=name,
        base_url=base_url,
        features=features,
    )

    # fill content stub with openai
    if use_openai:
        content = _fill_with_openai(base_url, content)

    # save content
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    print(f"[green]Created crawler for [b]{host}[/b]:[/green] [cyan]{file_path}[/cyan]")


def _build_path(locale: str, file_name: str):
    file_path = ctx.config.crawler.local_sources
    file_path /= locale or "multi"
    if locale == "en":
        file_path /= file_name[0]
    file_path /= file_name + ".py"
    return file_path


def _prompt_url() -> str:
    print("[i]The URL must start with [cyan]http[/cyan] or [cyan]https[/cyan].[/i]")
    return questionary.text(
        "Website URL:",
        qmark="🌐",
        validate=validate_url,
    ).ask()


def _prompt_locale() -> str:
    choices = [f"[{c:02}] {n}" for c, n in sorted(language_codes.items())]

    print("[i]Leave empty if locale is unknown or content is in multiple language:[/i]")
    language = questionary.autocomplete(
        "Enter language (ISO 639-1 code)",
        choices=choices,
        validate=lambda s: (s in choices) or (s in language_codes),
    ).ask()

    if len(language) > 2:
        language = language[1:3].strip()
    return language


def _prompt_features() -> List[Feature]:
    selected = questionary.checkbox(
        "Enable features:",
        choices=list(Feature),
    ).ask()
    return [Feature(v) for v in selected]


def _prompt_replace(file: str) -> bool:
    print(f"[i][cyan]{file}[/cyan][/i]")
    return questionary.confirm(
        "Crawler file already exists. Do you want to replace it?",
        default=False,
    ).ask()


def _prompt_use_openai() -> bool:
    return questionary.confirm(
        "Use OpenAI to auto-generate crawler?",
        default=bool(ctx.config.app.openai_key),
    ).ask()


def _prompt_openai_key() -> str:
    return questionary.text("OpenAI API Key").ask()


def _generate_stub(name: str, base_url: str, features: List[Feature]):
    content = """# -*- coding: utf-8 -*-
import logging
from typing import Iterable, Optional

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)

"""

    content += f"""
class {name}(BrowserTemplate):
    \"\"\"Scraper first; falls back to a real browser when requests fail.\"\"\"

    base_url = ["{base_url}"]
    has_manga = {Feature.has_manga in features}
    has_mtl = {Feature.has_mtl in features}
    can_login = {Feature.can_login in features}
    can_search = {Feature.can_search in features}
"""

    if Feature.can_search in features:
        content += """
    search_item_list_selector = ""
    search_item_title_selector = ""
    search_item_url_selector = ""
    search_item_info_selector = ""
"""

    content += """
    novel_title_selector = ""
    novel_cover_selector = ""
    novel_author_selector = ""
    novel_tags_selector = ""
    novel_synopsis_selector = ""
"""

    if Feature.has_volumes in features:
        content += """
    auto_create_volumes = False
    volume_list_selector = ""
    volume_title_selector = ""
"""

    content += """
    chapter_list_selector = ""
    chapter_title_selector = ""
    chapter_url_selector = ""
    chapter_body_selector = ""
"""

    content += """
    def initialize(self) -> None:
        # You can customize `TextCleaner` and other necessary things.
        super().initialize()
        self.taskman.init_executor(1)
"""

    if Feature.can_login in features:
        content += """
    def login(self, username_or_email: str, password_or_token: str) -> None:
        # Add logic to login when can_login is used.
        pass
"""

    if Feature.can_search in features:
        content += """
    def build_search_url(self, query: str) -> str:
        # URL of the search results page for the given query.
        # Example:
        # return f"{self.scraper.origin}search?q={query}"
        raise NotImplementedError()

    # Optional: set search_item_*_selector on the class, or override select_search_item_list().
"""

    if Feature.has_volumes in features:
        content += """
    def select_volume_tags(self, soup: PageSoup, novel: Novel) -> Iterable[PageSoup]:
        # Example: return soup.select("#toc .vol-item")
        return super().select_volume_tags(soup, novel)
"""

    content += """
    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        # When volume is set, soup is usually the volume block; otherwise the novel page.
        # Example: return soup.select("ul.chapter-list li a")
        return super().select_chapter_tags(soup, novel, volume)
"""

    return content


# Context for OpenAI: how Crawler / SoupTemplate / BrowserTemplate fit together (keep in sync with lncrawl.core).
_OPENAI_LNCRAWL_REFERENCE = """
### Class hierarchy
`Crawler` → `CrawlerTemplate` → `SoupTemplate` → `BrowserTemplate` (the generated class extends BrowserTemplate).

### Crawler (lncrawl.core.crawler) — excerpt
```python
class Crawler(ABC):
    base_url: Union[str, List[str]]
    has_mtl = False
    has_manga = False
    can_login = False
    can_search = False
    chapters_per_volume = 100
    auto_create_volumes = True  # False when the site has real volume sections; then use volume_* selectors

    def __init__(self, origin: str, workers: Optional[int] = None, parser: Optional[str] = None) -> None:
        # origin must match a normalized entry in base_url; creates self.scraper, self.taskman, self.cleaner

    def initialize(self) -> None: ...
    def login(self, username_or_email: str, password_or_token: str) -> None: ...

    @abstractmethod
    def read_novel(self, novel: Novel) -> None: ...

    @abstractmethod
    def download_chapter(self, chapter: Chapter) -> None: ...

    def absolute_url(self, url: Any, page_url: Optional[str] = None) -> str: ...
```

### SoupTemplate (lncrawl.core.template) — selectors drive defaults
Set class attributes; default `read_novel` / `download_chapter` / `search` call `parse_*` and `select_*` that use these selectors.

```python
class SoupTemplate(CrawlerTemplate):
    search_item_list_selector = ""
    search_item_title_selector = ""
    search_item_url_selector = ""
    search_item_info_selector = ""

    novel_title_selector = ""
    novel_cover_selector = ""
    novel_author_selector = ""
    novel_tags_selector = ""
    novel_synopsis_selector = ""

    volume_list_selector = ""
    volume_title_selector = ""

    chapter_list_selector = ""
    chapter_title_selector = ""
    chapter_url_selector = ""
    chapter_body_selector = ""

    def read_novel(self, novel: Novel) -> None:
        soup = self.scraper.get_soup(novel.url)
        self.parse_title(soup, novel)       # novel_title_selector → novel.title
        self.parse_cover(soup, novel)       # novel.cover_url
        self.parse_authors(soup, novel)     # novel.author (joined string)
        self.parse_tags(soup, novel)        # novel.tags (list)
        self.parse_summary(soup, novel)     # default sets novel.summary via cleaner.extract_contents
        self.parse_volume_list(soup, novel) # auto_create_volumes True: flat chapter list from novel page

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(chapter.url)
        body = soup.select_one(self.chapter_body_selector)
        self.parse_chapter_body(body, chapter)  # chapter.body = cleaner.extract_contents(soup)

    def build_search_url(self, query: str) -> str:
        raise NotImplementedError()

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        soup = self.scraper.get_soup(self.build_search_url(query))
        return soup.select(self.search_item_list_selector)

    def select_chapter_tags(self, soup, novel, volume=None) -> Iterable[PageSoup]:
        return soup.select(self.chapter_list_selector)
```

Override any `parse_*`, `select_*`, `build_search_url`, or `download_chapter` when selectors alone are insufficient.

### BrowserTemplate (lncrawl.core.browser) — excerpt
Extends SoupTemplate. Replaces `scraper.get_soup` (and `get_image`) so HTTP is tried first; on scrape failure it launches Chrome, visits the URL, and parses `browser.soup`. Requires browser support in config when fallback runs.

```python
class BrowserTemplate(SoupTemplate):
    def __init__(
        self,
        origin: str,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
        headless: bool = False,
        timeout: Optional[int] = 120,
    ) -> None:
        super().__init__(origin=origin, workers=workers, parser=parser)
        # patches get_soup / get_image for browser fallback
```

### Models & types (lncrawl.core)
- `Novel`: url, title, cover_url, author, tags, synopsis/summary, volumes, chapters, ...
- `Chapter`: id, url, title, volume (optional id), body
- `Volume`: id, title
- `SearchResult`: title, url, info
- `PageSoup`: soup nodes; use `.select` / `.select_one`, `.text`, `.get("href")`, etc.
"""


def _fill_with_openai(url: str, stub: str) -> str:
    client = OpenAI(api_key=ctx.config.app.openai_key)

    print(f"[i]Complete the stub from [cyan]{url}[/cyan][/i]")
    content_prompt = (
        f"You are given the URL of a novel-hosting website: `{url}`.\n\n"
        "Fetch the site content, find a representative novel page and a chapter page, then return a "
        "completed version of the class below.\n\n"
        "The crawler subclasses `BrowserTemplate` (lncrawl.core): HTTP first, browser fallback on failure. "
        "Under that is `SoupTemplate`, which already implements `read_novel`, `download_chapter`, and `search` "
        "using **class-level CSS selector strings** when those are set correctly.\n\n"
        "**Priority 1 — selectors (do these first):** Fill every selector attribute that appears in the stub "
        "with real CSS selectors so the default `SoupTemplate` behavior works. Use empty string only if the "
        "field truly does not exist on the site.\n\n"
        "- Search (if present): `search_item_list_selector`, `search_item_title_selector`, "
        "`search_item_url_selector`, `search_item_info_selector` (optional).\n"
        "- Novel page: `novel_title_selector`, `novel_cover_selector`, `novel_author_selector`, "
        "`novel_tags_selector`, `novel_synopsis_selector`.\n"
        "- Volumes (if present): `volume_list_selector`, `volume_title_selector`.\n"
        "- Chapters / body: `chapter_list_selector`, `chapter_title_selector`, `chapter_url_selector`, "
        "`chapter_body_selector`.\n\n"
        "**Priority 2 — overrides (only if selectors are not enough):** If the DOM needs logic that selectors "
        "cannot express (pagination, nested volumes, odd links, dynamic TOC, etc.), override the relevant "
        "`SoupTemplate` methods — for example `parse_title`, `parse_cover`, `parse_authors`, `parse_tags`, "
        "`parse_summary`, `select_volume_tags`, `parse_volume_title`, `select_chapter_tags`, "
        "`parse_chapter_title`, `parse_chapter_url`, `parse_chapter_body`, `build_search_url`, "
        "`select_search_item_list`, or `parse_search_item`. Keep using `super()` where the default "
        "implementation still applies.\n\n"
        + _OPENAI_LNCRAWL_REFERENCE
        + "\n### Stub to complete\n```\n"
        + stub
        + "\n```\n\nRequirements:\n"
        "- Output valid Python code only.\n"
        "- Do not include explanations, comments, or markdown fences.\n"
        "- Prefer filled selectors and minimal method bodies; override methods only when necessary.\n"
        "- Do not leave any unused imports.\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "Output Python code only. Prefer SoupTemplate CSS selector class attributes; override methods only when selectors are insufficient.",
                },
                {"role": "user", "content": content_prompt},
            ],
        )
        code = response.choices[0].message.content
        if not code:
            raise Exception("No code content in response")
        return code
    except Exception:
        logger.error("Failed to generate code", exc_info=True)
        return stub
