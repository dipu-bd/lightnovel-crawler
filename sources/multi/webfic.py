# -*- coding: utf-8 -*-
import logging
import json
import re

from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter, SearchResult

logger = logging.getLogger(__name__)


class Webfic(Crawler):
    """
        This site has multilingual novels, though just about all of them are paywalled unfortunately.

        The whole site obfuscates classes via Angular or some type of minifier
        so the only constant HTML comes from display text & HTML IDs
        But luckily all necessary data is stored in a consistent JSON that's always in the same script tag
    """
    base_url = ["https://www.webfic.com/"]
    has_manga = False
    has_mtl = False

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        metadata_json = soup.select_one('script#__NEXT_DATA__')
        metadata = json.loads(metadata_json.text)
        assert metadata  # this is where we get everything so it's kinda required

        self.novel_title = metadata['props']['pageProps']['bookInfo']['bookName']
        self.novel_cover = metadata['props']['pageProps']['bookInfo']['cover']
        try:
            self.novel_tags = metadata['props']['pageProps']['bookInfo']['tags']
        except KeyError:
            # the only one that has so far had an error, ever.
            pass
        self.novel_synopsis = metadata['props']['pageProps']['bookInfo']['introduction']
        self.novel_author = metadata['props']['pageProps']['bookInfo']['author']
        # available_langs = metadata['props']['pageProps']['languages']
        # true_chapter_count = metadata['props']['pageProps']['bookInfo']['chapterCount']

        logger.info("book metadata %s", metadata)

        lang, book_id = re.match("https://www.webfic.com(/?.*)/book_info/(\\d+)/.*", self.novel_url).groups()
        self.language = "en"
        if lang:
            logger.info("Novel is not english, instead is: %s", lang)
            self.language = lang[1:]

        cinfo_template = f"https://www.webfic.com{lang}/catalog/{book_id}/"
        found_premium = False
        chapters = []
        cinfo_idx = 1

        while not found_premium:
            cinfo_link = f"{cinfo_template}{cinfo_idx}"
            cinfo_soup = self.get_soup(cinfo_link)
            cinfo_meta = cinfo_soup.select_one("script#__NEXT_DATA__")
            assert cinfo_meta
            cinfo_info = json.loads(cinfo_meta.text)
            cinfo_pages = cinfo_info['props']['pageProps']['totalPage']
            cinfo_idx += 1
            # in theory if all chapters are free it should reach here and break out
            if cinfo_idx > cinfo_pages:
                break

            for chap in cinfo_info['props']['pageProps']['chapterList']:
                # ignore premium chapters as they're "app-walled"
                if not chap["unlock"]:
                    found_premium = True
                    break
                # chapter link template https://www.webfic.com/book/<bookid>/<chapid>
                chapters.append(
                    {"url": f"https://www.webfic.com{lang}/book/{book_id}/{chap['id']}", "title": chap["chapterName"]})

        for idx, chapter in enumerate(chapters):
            chap_id = 1 + idx
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            if chap_id % 100 == 1:
                self.volumes.append(
                    Volume(
                        id=vol_id,
                        title=vol_title
                    ))

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=chapter["url"],
                    title=chapter["title"],
                    volume=vol_id,
                    volume_title=vol_title
                ),
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)

        chapter_metadata = soup.select_one("script#__NEXT_DATA__")
        chapter = json.loads(chapter_metadata.text)
        assert chapter

        logger.info("chapeter %s", chapter)

        text_lines = chapter['props']['pageProps']['chapterInfo']['content'].split("\n")

        # copied straight outta self.cleaner.extract_contents because we lack a TAG...
        # otherwise the output looks very mushed together cause it ignores all the newlines otherwise
        text = "".join(
            [
                f"<p>{t.strip()}</p>"
                for t in text_lines
                if not self.cleaner.contains_bad_texts(t)
            ]
        )

        return text

    def search_novel(self, query: str):
        query_simple_encoded = query.replace(' ', '+')
        soup = self.get_soup(f"https://www.webfic.com/search?searchValue={query_simple_encoded}")
        results = []

        metadata_json = soup.select_one('script#__NEXT_DATA__')
        metadata = json.loads(metadata_json.text)
        assert metadata  # this is where we get everything so it's kinda required
        logger.info("search results metadata: %s", metadata)

        data = metadata["props"]["pageProps"]
        novels = data["total"]
        pages = data["pages"]

        # 0 novels -> nothing found
        if not novels:
            return []

        for page_idx in range(pages):
            page = 1 + page_idx
            soup_page = self.get_soup(f"https://www.webfic.com/search/{page}?searchValue={query_simple_encoded}")
            m_page_json = soup_page.select_one('script#__NEXT_DATA__')
            m_page = json.loads(m_page_json.text)
            data_page = m_page["props"]["pageProps"]

            for novel in data_page["bookList"]:
                novel_id = novel["bookId"]
                novel_title = novel["bookName"]
                novel_uri_name = novel["replacedBookName"]
                novel_info = {
                    "Ratings": novel["ratings"],
                    "Chapters": novel["chapterCount"],
                    "Status": novel["writeStatus"],
                    "Premium": self.premium_idx_to_text(novel["free"]),
                    "Audience": novel["targetAudience"],

                }
                results.append(
                    SearchResult(
                        title=novel_title,
                        url=f"https://www.webfic.com/book_info/{novel_id}/all/{novel_uri_name}",
                        info=" | ".join([f"{key}: {value}" for key, value in novel_info.items()])
                    )
                )
            pass
        return results

    @staticmethod
    def premium_idx_to_text(idx):
        if idx == 2:
            return "Partial Paywall"
        else:
            return "Unknown"
