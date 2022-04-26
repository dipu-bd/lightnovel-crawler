import sys
from pathlib import Path

cur_dir = Path(__file__).parent

try:
    sys.path.insert(0, str(cur_dir.parent.absolute()))
    from lncrawl.core.crawler import Crawler
except ImportError as e:
    exit(1)


class TestCrawler(Crawler):
    def read_novel_info(self):
        pass

    def download_chapter_body(self, chapter):
        pass

    def test_sample1(self):
        with open(cur_dir / 'data' / 'sample1.html', encoding='utf8') as f:
            html_text = f.read()
        soup = self.make_soup(html_text)
        chapter = soup.select_one('article #chapter')
        text = self.cleaner.extract_contents(chapter)
        print(text)

    def test_sample2(self):
        with open(cur_dir / 'data' / 'sample2.html', encoding='utf8') as f:
            html_text = f.read()
        soup = self.make_soup(html_text)
        chapter = soup.select_one('article')
        text = self.cleaner.extract_contents(chapter)
        print(text)


if __name__ == '__main__':
    #TestCrawler().test_sample1()
    TestCrawler().test_sample2()
