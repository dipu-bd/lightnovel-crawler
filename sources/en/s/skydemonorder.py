import json
import logging
import re

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)


class SkyDemonOrder(LegacyCrawler):
    base_url = "https://skydemonorder.com"

    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1").text.strip()
        assert possible_title, "No novel title"
        self.novel_title = possible_title
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(f"img[alt='{self.novel_title}']")
        if possible_image:
            self.novel_cover = possible_image["src"]
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract CSRF token for Livewire request
        csrf_meta = soup.select_one('meta[name="csrf-token"]')
        assert csrf_meta, "No CSRF token found"
        csrf_token = csrf_meta["content"]

        # Extract Livewire update URL from script tag
        lw_script = soup.select_one('script[src*="livewire"]')
        assert lw_script, "No Livewire script tag found"
        lw_match = re.search(r"(livewire-[a-f0-9]+)", lw_script["src"])
        assert lw_match, "Could not extract Livewire path"
        livewire_url = self.absolute_url(f"/{lw_match.group(1)}/update")

        # Extract snapshot from the lazy-loaded chapter-list component
        lw_div = soup.find("div", attrs={"wire:name": "project.chapter-list"})
        assert lw_div, "No Livewire chapter-list component found"
        snapshot = lw_div["wire:snapshot"]

        # Fetch chapter list via Livewire lazy-load
        lw_response = self.post_json(
            livewire_url,
            data={"components": [{"snapshot": snapshot, "updates": {}, "calls": []}]},
            headers={"X-CSRF-TOKEN": csrf_token, "X-Livewire": ""},
        )

        chapter_html = lw_response["components"][0]["effects"]["html"]
        chapter_soup = self.make_soup(chapter_html)

        # Parse chapter data from Alpine.js x-data in the response
        xdata_div = chapter_soup.select_one("div[x-data]")
        assert xdata_div, "No x-data div in chapter list response"
        x_data = xdata_div["x-data"]

        free_match = re.search(r"freeChapters:\s*JSON\.parse\('(.+?)'\)", x_data)
        assert free_match, "Could not extract freeChapters from x-data"
        # Decode JS string escapes before parsing JSON
        raw_json = re.sub(
            r"\\u([0-9a-fA-F]{4})",
            lambda m: chr(int(m.group(1), 16)),
            free_match.group(1),
        )
        raw_json = raw_json.replace("\\'", "'")
        chapters = json.loads(raw_json)

        slug_match = re.search(r"projectSlug:\s*'([^']+)'", x_data)
        assert slug_match, "Could not extract projectSlug from x-data"
        project_slug = slug_match.group(1)

        chapters.reverse()

        for item in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100

            if len(self.volumes) < vol_id:
                self.volumes.append(Volume(id=vol_id))

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    url=self._make_url(item["slug"], project_slug),
                    title=item["title"],
                )
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".prose")

        return self.cleaner.extract_contents(contents)

    def _make_url(self, slug, project_slug):
        return self.absolute_url("/" + "projects" + "/" + project_slug + "/" + slug)
