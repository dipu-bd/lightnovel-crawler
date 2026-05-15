from lncrawl.core import BrowserTemplate, Chapter, Volume


class NovelCool(BrowserTemplate):
    has_manga = True
    base_url = "https://www.novelcool.com/"

    novel_title_selector = "h1.bookinfo-title"
    novel_author_selector = ".bookinfo-author a"
    novel_cover_selector = ".bookinfo-pic img"
    novel_synopsis_selector = ".bk-summary-txt"
    novel_tags_selector = ".bookinfo-category-list a"
    chapter_list_selector = ".chapter-item-list a"
    chapter_title_selector = ".chapter-item-title"
    chapter_list_reverse = True

    def initialize(self):
        self.cleaner.bad_css.update(
            {
                ".chapter-title",
                ".chapter-start-mark",
                ".chapter-end-mark",
                'div[model_target_name="report"]',
            }
        )

    def download_chapter(self, chapter: Chapter):
        soup = self.scraper.get_soup(chapter["url"])
        content = soup.select_one(".chapter-start-mark").parent
        chapter.body = self.cleaner.extract_contents(content)
