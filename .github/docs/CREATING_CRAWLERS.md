# Creating Source Crawlers

This is the canonical guide for adding support for new novel sources to Lightnovel Crawler.

---

## What is a source crawler?

A **source crawler** is a small Python script that tells Lightnovel Crawler how to read a specific novel website. It answers two main questions:

1. **What’s on the novel page?** — title, author, cover, list of chapters.
2. **What’s inside each chapter?** — the actual chapter text, cleaned of ads and navigation.

Once you add a crawler, users can download novels from that site through the app or the web UI.

## What you’ll need

- **Python 3** and the project set up (clone the repo, then `make install` or `uv sync --all-extras --all-groups`).
- **The novel site’s URL** you want to support.
- **Basic familiarity with HTML** — you’ll use CSS selectors (e.g. `div.chapter-content`) to pick elements. No need to be an expert; you can copy from existing crawlers and tweak.

> **New to the project?** From the repo root run `make install` (or `uv sync --all-extras --all-groups`). See the main README and root `Makefile` for setup.

---

## Recommended: start from the soup template

The **easiest and most maintainable** way to add a new crawler is to use the **GeneralSoupTemplate** and copy the official example:

1. **Copy** `sources/_examples/_01_general_soup.py` into the right folder (e.g. `sources/en/m/mysite.py`).
2. **Rename** the class (e.g. `MySiteCrawler`) and set `base_url` to your site’s domain(s).
3. **Implement** the required methods: `parse_title`, `parse_cover`, `parse_chapter_list`, and `select_chapter_body`. The template handles the rest (fetching pages, cleaning, building the novel).
4. **Test** with a real novel URL.

This approach uses small, focused methods (one per piece of data) instead of one big `read_novel_info`. The rest of this guide explains each method and shows examples. If you need search, volumes, or browser-based scraping, see the other files in `sources/_examples/` (e.g. `_02_searchable_soup.py`, `_05_with_volume_soup.py`).

## Quick Start (the big picture)

1. **Create a new file** in the right folder under `sources/` (e.g. `sources/en/m/mysite.py`).
2. **Use GeneralSoupTemplate** (from `lncrawl.templates.soup.general`) and set your site’s URL(s) in `base_url`.
3. **Implement four required methods:** `parse_title`, `parse_cover`, `parse_chapter_list`, and `select_chapter_body`.
4. **Test locally** with a real novel URL.

The rest of this guide walks you through each step in detail.

---

## Where to put your file

Crawlers are grouped by language. Pick the folder that matches your site:

| Site language | Folder                             | Example path              |
| ------------- | ---------------------------------- | ------------------------- |
| English       | `sources/en/` then by first letter | `sources/en/m/mysite.py`  |
| Chinese       | `sources/zh/`                      | `sources/zh/mysite.py`    |
| Japanese      | `sources/ja/`                      | `sources/ja/mysite.py`    |
| Multiple      | `sources/multi/`                   | `sources/multi/mysite.py` |

**English sites:** use a letter subfolder based on the site name (e.g. “My Novel Site” → `sources/en/m/`). This keeps the list easy to browse.

**File name:** use something that identifies the site, e.g. `mysite.py`, `novelhub.py`. Avoid generic names like `crawler.py`.

## Basic structure (GeneralSoupTemplate)

Every crawler is a single Python file with a class that **inherits from `GeneralSoupTemplate`**. You set `base_url` and implement four methods; the template takes care of fetching pages and wiring everything together. Here’s a minimal skeleton (or copy `sources/_examples/_01_general_soup.py` and remove the optional bits):

```python
# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, Volume
from lncrawl.templates.soup.general import GeneralSoupTemplate

logger = logging.getLogger(__name__)


class MySiteCrawler(GeneralSoupTemplate):
    base_url = ["https://mysite.com/", "https://www.mysite.com/"]

    def parse_title(self, soup: BeautifulSoup) -> str:
        """Return the novel title from the novel page."""
        raise NotImplementedError()  # e.g. return soup.select_one("h1.title").get_text(strip=True)

    def parse_cover(self, soup: BeautifulSoup) -> Optional[str]:
        """Return the cover image URL, or '' if none."""
        return ""

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        """Yield Volume and Chapter objects. Template appends them to self.volumes / self.chapters."""
        yield from []

    def select_chapter_body(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Return the Tag that contains the chapter text (soup is the chapter page)."""
        raise NotImplementedError()  # e.g. return soup.select_one(".chapter-content")
```

**What each part does:**

- **`base_url`** — When a user pastes a URL, the app checks this list. If the URL starts with one of these, your crawler is used.
- **`parse_title(soup)`** — Given the novel page HTML (as BeautifulSoup), return the title string.
- **`parse_cover(soup)`** — Return the cover image URL or `''`. Use `self.absolute_url(...)` for relative URLs.
- **`parse_chapter_list(soup)`** — Yield `Volume` and/or `Chapter` objects in order. The template adds them to `self.volumes` and `self.chapters`.
- **`select_chapter_body(soup)`** — Given the **chapter page** HTML, return the single Tag that wraps the story text. The template will clean and extract it.

The template calls `get_novel_soup()` to get the novel page (default: `self.get_soup(self.novel_url)`). You can override it if the novel page needs a different URL or POST request.

## Required method 1: `parse_title(self, soup)`

**In plain English:** The template gives you the novel page as a BeautifulSoup object. Return the novel’s title as a string.

**Example:** Change the selector to match your site (use the browser’s “Inspect” tool).

```python
def parse_title(self, soup: BeautifulSoup) -> str:
    tag = soup.select_one("h1.title")  # or "h1", ".novel-title", etc.
    return tag.get_text(strip=True) if tag else ""
```

## Required method 2: `parse_cover(self, soup)`

**In plain English:** Return the cover image URL from the novel page. Use `self.absolute_url(...)` for relative URLs. Return `''` or `None` if there’s no cover.

```python
def parse_cover(self, soup: BeautifulSoup) -> Optional[str]:
    img = soup.select_one("img.cover")  # or "img#cover", etc.
    if img and img.get("src"):
        return self.absolute_url(img["src"])
    return ""
```

## Required method 3: `parse_chapter_list(self, soup)`

**In plain English:** From the novel page, yield `Volume` and `Chapter` objects in order. The template appends them to `self.volumes` and `self.chapters`. You can yield only `Chapter` objects (no volumes); the app will still work.

**Chapter** has: `id`, `title`, `url` (and optionally `volume`). **Volume** has: `id`, `title`.

**Example:** Site has a flat list of chapter links. We auto-create one volume and yield chapters.

```python
from lncrawl.models import Chapter, Volume

def parse_chapter_list(
    self, soup: BeautifulSoup
) -> Generator[Union[Chapter, Volume], None, None]:
    # One volume for simplicity
    yield Volume(id=1, title="Volume 1")

    for idx, a in enumerate(soup.select("ul.chapters a"), 1):
        yield Chapter(
            id=idx,
            title=a.get_text(strip=True),
            url=self.absolute_url(a["href"]),
            volume=1,
        )
```

If the site has explicit volume headings, yield a `Volume` before each group of chapters and set `volume=vol_id` on each `Chapter`.

## Required method 4: `select_chapter_body(self, soup)`

**In plain English:** The template fetches the chapter page and passes it as `soup`. Return the **single Tag** that contains the chapter text (the template will clean and extract it). Return `None` if not found.

**Example:** Change the selector to match your site’s chapter content wrapper.

```python
def select_chapter_body(self, soup: BeautifulSoup) -> Optional[Tag]:
    return soup.select_one("div.chapter-content")  # or ".m-read .txt", etc.
```

---

## Optional methods (GeneralSoupTemplate)

You can override these in the same file when needed; otherwise the template’s default is used.

| Method                                              | Purpose                                                                                                                               |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `get_novel_soup(self)`                              | Return the BeautifulSoup for the novel page (default: `self.get_soup(self.novel_url)`). Override if you need a different URL or POST. |
| `parse_authors(self, soup)`                         | Yield author strings. Default: yields nothing.                                                                                        |
| `parse_genres(self, soup)`                          | Yield genre/tag strings. Default: yields nothing.                                                                                     |
| `parse_summary(self, soup)`                         | Return the novel summary/synopsis. Default: `''`.                                                                                     |
| `initialize(self)`                                  | One-time setup (cleaner rules, headers).                                                                                              |
| `login(self, username_or_email, password_or_token)` | Log in before scraping, if the site requires it.                                                                                      |

**Example — parse_authors:**

```python
def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
    tag = soup.find("strong", string="Author:")
    if tag and tag.next_sibling:
        yield tag.next_sibling.get_text(strip=True)
    # Or: for a in soup.select(".author a"): yield a.get_text(strip=True)
```

---

## Alternative: base Crawler (manual style)

If you prefer to control everything yourself (one big `read_novel_info` and `download_chapter_body`), you can inherit from **`Crawler`** instead. Copy `sources/_examples/_00_basic.py` and implement:

- `read_novel_info(self)` — set `self.novel_title`, `self.novel_cover`, `self.novel_author`, `self.volumes`, `self.chapters`.
- `download_chapter_body(self, chapter)` — return the chapter HTML string.

This style is still supported but the **GeneralSoupTemplate** style is recommended for new crawlers (smaller methods, less boilerplate, same result).

## Helpers you’ll use (quick reference)

The base template gives you these. You’ll use them inside your `parse_*` and `select_chapter_body` methods.

### HTTP and parsing

| Method                        | Description                         |
| ----------------------------- | ----------------------------------- |
| `self.get_soup(url)`          | GET request, returns BeautifulSoup  |
| `self.post_soup(url, data)`   | POST request, returns BeautifulSoup |
| `self.get_json(url)`          | GET request, returns JSON           |
| `self.post_json(url, data)`   | POST request, returns JSON          |
| `self.submit_form(url, data)` | Submit form data                    |

### URLs

| Method                    | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `self.absolute_url(path)` | Turn a relative link (e.g. `/chapter/1`) into a full URL |
| `self.novel_url`          | The novel page URL the user opened                       |

### Content cleaning

Sites often wrap chapter text in extra divs, ads, and scripts. Use `self.cleaner` to strip those and get only the story text:

```python
# Remove specific CSS selectors
self.cleaner.bad_css.update(["div.ads", "span.watermark"])

# Remove specific tags
self.cleaner.bad_tags.update(["script", "style"])

# Extract clean content
html = self.cleaner.extract_contents(soup_element)
```

## Choosing the right example

**Start here:** For most sites (simple novel pages, no search or fancy JS), copy **`sources/_examples/_01_general_soup.py`** and implement the four required methods. That’s the recommended approach.

**Need search?** If the site has a search box and you want users to search by name, use **`_02_searchable_soup.py`** (SearchableSoupTemplate). You’ll implement `select_search_items`, `parse_search_item`, plus the same parse methods as above.

**Sites with volumes:** If the page has explicit volume blocks, use **`_05_with_volume_soup.py`** or **`_07_optional_volume_soup.py`** and implement `parse_volume_item` / `parse_chapter_item` as in those files.

**JavaScript-heavy sites:** If the novel or chapter content is loaded by JavaScript, use one of the browser templates in `sources/_examples/` (e.g. `_09_basic_browser.py`, `_10_general_browser.py`). They use a headless browser to render the page before parsing.

**Known engine (Madara, NovelFull, etc.):** If your site looks like a known engine (same HTML structure as many other sites), you can inherit from `lncrawl.templates.madara`, `lncrawl.templates.novelfull`, or `lncrawl.templates.novelpub` and mostly set `base_url` and override only what differs. See existing crawlers in `sources/` that use those templates.

---

## Testing your crawler

Run these from the **project root** (where `Makefile` and `pyproject.toml` live).

1. **One-time setup** (if you haven’t already). This installs dependencies with [uv](https://docs.astral.sh/uv/):

   ```bash
   make install
   # or: uv sync --all-extras --all-groups
   ```

2. **Run a quick download test.** Replace the URL with a real novel URL from your site. `--first 3` only downloads 3 chapters; `-f` overwrites existing output:

   ```bash
   uv run python -m lncrawl -s "https://mysite.com/novel/example" --first 3 -f
   ```

   **What to expect:** The app will use your crawler, fetch the novel info and 3 chapters, and save them (e.g. in an `output` folder or as specified by the app). If you see errors about selectors or “element not found”, your CSS selectors don’t match the site — use the browser’s Inspect tool to find the correct class names.

3. **Confirm your crawler is registered.** Your file should appear in the sources list:

   ```bash
   uv run python -m lncrawl sources list | grep mysite
   ```

   Replace `mysite` with part of your crawler’s filename or site name. If nothing appears, check that the file is in the right `sources/` folder and that the class inherits from `Crawler` (or a template).

## Best practices

1. **Log useful info** so you can debug later:  
   `logger.info("Found %d chapters", len(self.chapters))`

2. **Handle missing data** — not every novel has a cover or author. Use `if element:` before accessing attributes.

3. **Respect the site** — don’t send too many requests at once; the base app already limits concurrency.

4. **Test a few novels** — try one with many chapters, one with special characters in the title, and one with no cover to catch edge cases.

5. **Clean the content** — use `self.cleaner` to strip ads, “next chapter” links, and scripts so the final ebook looks clean.

### Common mistakes

- **Wrong selectors** — The site’s HTML might use different class names. Inspect the page in your browser and match the exact tags and classes.
- **Relative URLs** — Use `self.absolute_url(link["href"])` for chapter URLs and the cover image so they work when the app downloads them.
- **Leaving required methods unimplemented** — Make sure `parse_title`, `parse_cover`, `parse_chapter_list`, and `select_chapter_body` return real data (and that `parse_chapter_list` yields at least one chapter); otherwise the app will do nothing.

---

## Full example (GeneralSoupTemplate)

Below is a complete crawler using **GeneralSoupTemplate**. Replace the selectors with the ones that match your target site. You can get the same result by copying `sources/_examples/_01_general_soup.py` and filling in the TODOs.

```python
# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, Volume
from lncrawl.templates.soup.general import GeneralSoupTemplate

logger = logging.getLogger(__name__)


class ExampleCrawler(GeneralSoupTemplate):
    base_url = ["https://example-novel-site.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["div.advertisement", "div.social-share"])

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1.novel-title")
        return tag.get_text(strip=True) if tag else ""

    def parse_cover(self, soup: BeautifulSoup) -> Optional[str]:
        img = soup.select_one("img.novel-cover")
        if img and img.get("src"):
            return self.absolute_url(img["src"])
        return ""

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        author = soup.select_one("span.author-name")
        if author:
            yield author.get_text(strip=True)

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        yield Volume(id=1, title="Volume 1")
        links = soup.select("ul.chapter-list a")
        for idx, a in enumerate(links, 1):
            yield Chapter(
                id=idx,
                title=a.get_text(strip=True),
                url=self.absolute_url(a["href"]),
                volume=1,
            )
        logger.info("Found %d chapters", len(links))

    def select_chapter_body(self, soup: BeautifulSoup) -> Optional[Tag]:
        return soup.select_one("div.chapter-content")
```

---

**Next steps:** Start from **`sources/_examples/_01_general_soup.py`**, implement the four required methods for your site, then test with `uv run python -m lncrawl -s "URL" --first 3 -f`. For search, volumes, or browser-based scraping, use the other numbered examples in `sources/_examples/`. When everything works, open a pull request to add your crawler to the main project.
