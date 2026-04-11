# -*- coding: utf-8 -*-
import logging
from collections import Counter
from urllib.parse import urlencode

from lncrawl.core import Crawler
from lncrawl.models import Chapter

logger = logging.getLogger(__name__)


class RanobeLibMeCrawler(Crawler):
    base_url = [
        "https://ranobelib.me/",
    ]

    def initialize(self):
        self.init_executor(ratelimit=0.99)
        self.scraper.headers["Site-Id"] = "3"
        clean_url = self.novel_url.split("?")[0].strip("/")
        self.api_url = f"https://api.cdnlibs.org/api/manga/{clean_url.split('/')[-1]}"

    def read_novel_info(self):
        api_requests_params = {
            "fields[]": [
                "background",
                "eng_name",
                "otherNames",
                "summary",
                "genres",
                "chap_count",
                "status_id",
                "authors",
                "format",
            ]
        }

        logger.debug("Visiting %s", self.novel_url)
        book_info = self.get_json(f"{self.api_url}?{urlencode(api_requests_params, doseq=True)}")

        self.novel_title = book_info["data"]["rus_name"]
        logger.info("Novel title: %s", self.novel_title)

        novel_cover = book_info["data"]["cover"]["default"]
        if "https" not in novel_cover:
            novel_cover = f"https://ranobelib.me/{novel_cover}"
        self.novel_cover = novel_cover
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = book_info["data"]["authors"][0]["name"]
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = book_info["data"]["summary"]
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        genres = book_info["data"]["genres"]
        self.novel_tags = [item["name"] for item in genres]
        logger.info("Novel tags: %s", self.novel_tags)

        chapters = self.get_json(f"{self.api_url}/chapters")["data"]

        # Count chapters per branch and collect all team names
        branch_counts = Counter()
        branch_teams = {}
        for chapter in chapters:
            for b in chapter["branches"]:
                bid = b["branch_id"]
                branch_counts[bid] += 1
                if bid not in branch_teams:
                    branch_teams[bid] = set()
                for t in b.get("teams", []):
                    name = t.get("name", "").strip()
                    if name:
                        branch_teams[bid].add(name)

        # Let the user set branch priorities by sequential selection
        if len(branch_counts) > 1:
            remaining = [
                (bid, count) for bid, count in branch_counts.most_common()
            ]
            priority = []

            while remaining:
                print()
                if not priority:
                    print("Select primary translation:")
                else:
                    print(f"Next priority ({len(priority)} selected):")
                for i, (bid, count) in enumerate(remaining, 1):
                    teams = ", ".join(sorted(branch_teams.get(bid, set()))) or f"Branch {bid}"
                    print(f"  {i}) {teams} ({count} chapters)")
                if priority:
                    print(f"  0) Done")

                try:
                    raw = input("Choice: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if raw == "0" and priority:
                    break

                try:
                    idx = int(raw) - 1
                    if 0 <= idx < len(remaining):
                        pick = remaining.pop(idx)
                        priority.append(pick[0])
                    else:
                        print("Invalid number")
                except ValueError:
                    print("Enter a number")

            if not priority:
                raise SystemExit("Cancelled by user")
        elif branch_counts:
            priority = [next(iter(branch_counts))]
        else:
            priority = []

        chap_id = 0
        for chapter in chapters:
            if any("moderation" in cb for cb in chapter["branches"]):
                continue

            # Pick the highest-priority branch available for this chapter
            available = {cb["branch_id"] for cb in chapter["branches"]}
            branch = next((bid for bid in priority if bid in available), None)
            if branch is None:
                continue

            chap_id += 1
            chap_num = chapter["number"]

            params = {
                "volume": chapter["volume"],
                "number": chapter["number"],
                "branch_id": branch,
            }

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=f"{self.api_url}/chapter?{urlencode(params, doseq=True)}",
                    title=chapter["name"] or f"Chapter {chap_num}",
                )
            )

    def download_chapter_body(self, chapter):
        chapter = self.get_json(chapter["url"])

        if "content" in chapter["data"]["content"]:
            paragraphs = self._paragraph_parser(data=chapter["data"])
            chapter_content = "".join(
                [f"<p>{text['text']}</p>" for tag in paragraphs for text in tag if "text" in text]
            )
            return chapter_content

        else:
            chapter_content = self.make_soup(chapter["data"]["content"])
            return self.cleaner.extract_contents(chapter_content)

    def _paragraph_parser(self, data):
        paragraphs = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key == "type" and value == "paragraph":
                    paragraphs.append(data.get("content", ""))
                else:
                    paragraphs.extend(self._paragraph_parser(value))

        elif isinstance(data, list):
            for item in data:
                paragraphs.extend(self._paragraph_parser(item))

        return paragraphs
