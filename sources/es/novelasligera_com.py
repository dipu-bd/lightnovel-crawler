# -*- coding: utf-8 -*-
from lncrawl.core import BrowserTemplate, Chapter, Novel


class NovelasLigeraCrawler(BrowserTemplate):
    base_url = ["https://novelasligera.com/"]
    has_manga = False
    has_mtl = False

    novel_title_selector = "h1.entry-title"
    novel_cover_selector = ".elementor-widget-container img"
    chapter_list_selector = ",".join(
        [
            "div.elementor-tab-content ul.lcp_catlist li a[href]",
            "div.elementor-accordion ul.lcp_catlist li a[href]",
            "ul.lcp_catlist li a[href]",
        ]
    )
    chapter_body_selector = "div.entry-content"

    def initialize(self) -> None:
        super().initialize()
        self.cleaner.bad_tags.update(
            [
                "script",
                "style",
                "noscript",
                "iframe",
            ]
        )
        self.cleaner.bad_css.update(
            [
                ".osny-nightmode",
                ".code-block",
                ".zeno_font_resizer_container",
                ".sharedaddy",
                ".jp-relatedposts",
                ".saboxplugin-wrap",
                ".post-ratings",
                ".post-tags",
                ".entry-meta",
                ".author-box",
                ".yarpp-related",
            ]
        )

    def read_novel(self, novel: Novel) -> None:
        soup = self.get_novel_soup(novel)
        self.parse_title(soup, novel)
        self.parse_cover(soup, novel)
        self.parse_summary(soup, novel)

        for container in soup.select(self.novel_author_selector):
            for p in container.find_all("p"):
                text = p.get_text(" ", strip=True)
                if "Autor:" in text:
                    novel.author = text.split("Autor:", 1)[1].strip()
                elif "Género:" in text:
                    genres_text = text.split("Género:", 1)[1].strip().rstrip(".")
                    novel.genres = [g.strip() for g in genres_text.split(",") if g.strip()]

        seen_urls = set()
        for a in soup.select(self.chapter_list_selector):
            title = a.get_text(" ", strip=True)
            url = self.absolute_url(a.get("href"))
            if not url or not title or url in seen_urls:
                continue

            seen_urls.add(url)
            chapter = Chapter(
                id=len(novel.chapters) + 1,
                url=url,
                title=title,
            )
            novel.chapters.append(chapter)
