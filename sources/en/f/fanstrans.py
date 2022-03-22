# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class FansTranslations(Crawler):
    base_url = 'https://fanstranslations.com/'

    def initialize(self) -> None:
        self.cleaner.blacklist_patterns.update([
            r'^Translator Thoughts:',
            r'^Please leave some comments to show your support~',
            r'^Please some some positive reviews on NovelUpate',
            r'^AI CONTENT END 2',
            r'^Please leave some some positive reviews on Novel Updates',
            r'^Check how can you can have me release Bonus Chapters',
            r'^Please subscribe to the blog ~',
            r'^Please click on the ad in the sidebar to show your support~',
            r'^Access to advance chapters and support me',
            r'^Access to 2 advance chapters and support me',
            r'^Check out other novels on Fan’s Translation ~',
            r'^Support on Ko-fi',
            r'^Get  on Patreon',
            r'^Check out other novels on Fan’s Translation~',
            r'^to get Notification for latest Chapter Releases',
        ])
        self.cleaner.bad_tags.update(['a'])
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('h1.page-header-title')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('#editdescription p span img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "by Fans Translations"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        chapters = soup.select('div.entry div a[href*="fanstranslations.com"]')

        vols = set([])
        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters)//100 + 1
            vols.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip(),
            })
        # end for

        self.volumes = [{'id': x} for x in vols]
    # end def


    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        body_parts = soup.select_one('.site-content .entry-content')

        # TODO: Can't remove some junk text because it contains &#160; and I can't find a way to remove it.

        for content in body_parts.select("p"):
            for bad in ["&#160;And", "Support on", "and Join", "<span>And</span>"]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(body_parts)
    # end def
# end class
