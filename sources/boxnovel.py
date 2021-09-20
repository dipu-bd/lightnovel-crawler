# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://boxnovel.com/?s=%s&post_type=wp-manga&author=&artist=&release='

class BoxNovelCrawler(Crawler):
    base_url = 'https://boxnovel.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h4 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('meta[property="og:title"]')['content']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = soup.select_one('meta[property="og:image"]')['content']
        logger.info('Novel cover: %s', self.novel_cover)

        try:
            author = soup.select('.author-content a')
            if len(author) == 2:
                self.novel_author = author[0].text + ' (' + author[1].text + ')'
            else:
                self.novel_author = author[0].text
        except Exception as e:
            logger.debug('Failed to parse novel author. Error: %s', e)
        logger.info('Novel author: %s', self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(self.novel_url.strip('/') + '/ajax/chapters')
        soup = self.make_soup(response)
        for a in reversed(soup.select(".wp-manga-chapter a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            # end if
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('div.text-left')
        return self.extract_contents(contents)
    # end def
# end class
