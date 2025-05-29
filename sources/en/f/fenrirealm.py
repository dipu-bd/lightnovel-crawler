# -*- coding: utf-8 -*-
import logging
import json
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class FenriRealm(Crawler):
    base_url = [
        "https://fenrirealm.com/",
    ]

    def search_novel(self, query):
        search_url = f"{self.home_url.rstrip('/')}/api/novels/filter?page=1&per_page=10&search={query}"
        response = self.get_response(search_url).text
        data = json.loads(response)

        results = []
        if data and "data" in data:
            for novel in data["data"]:
                results.append(
                    {
                        "title": novel["title"],
                        "url": f"{self.home_url.rstrip('/')}/series/{novel['slug']}",
                        "info": f"Author: {novel['user']['name']}, Status: {novel['status']}",
                    }
                )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        regex = re.compile(r"const data = (.*;.*);")
        match = regex.search(str(soup))
        js_dict = match.group(1)

        # Extract novel title
        title_match = re.search(r'title:"([^"]+)"', js_dict)
        if title_match:
            self.novel_title = title_match.group(1)

        # Extract novel author (assuming it's in the user field)
        author_match = re.search(r'user:{username:"([^"]+)"', js_dict)
        if author_match:
            self.novel_author = author_match.group(1)

        # Extract novel cover
        cover_match = re.search(r'cover:"([^"]+)"', js_dict)
        if cover_match:
            self.novel_cover = self.home_url.rstrip("/") + "/" + cover_match.group(1)

        # Extract novel synopsis
        synopsis_match = re.search(r'description:"([^"]+)"', js_dict)
        if synopsis_match:
            self.novel_synopsis = synopsis_match.group(1)

        # Extract novel tags
        tags_match = re.search(r"tags:\[(.*?)\]", js_dict)
        if tags_match:
            tags_text = tags_match.group(1)
            tag_names = re.findall(r'name:"([^"]+)"', tags_text)
            self.novel_tags = tag_names

        # Get chapter list from API
        chapter_list_url = self.novel_url.replace("series", "api/novels/chapter-list")
        response = self.get_response(chapter_list_url).text
        chapters_data = json.loads(response)

        # Reverse the order of chapters (API returns newest first)
        chapters_data.sort(key=lambda x: x["number"])

        # Add volumes and chapters
        for chapter in chapters_data:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100

            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            slug = chapter.get("slug", "")
            name = chapter.get("name", "")
            title = chapter.get("title", "")

            # Format chapter title
            chapter_title = name
            if title and title.strip():
                chapter_title += f" - {title}"

            # Create chapter URL
            novel_slug = self.novel_url.split("/")[-1]
            chapter_url = f"{self.home_url.rstrip('/')}/series/{novel_slug}/{slug}"

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": chapter_title,
                    "url": chapter_url,
                }
            )

    def download_chapter_body(self, chapter):
        return self.cleaner.extract_contents(
            self.get_soup(chapter.url).select_one("div#reader-area")
        )
