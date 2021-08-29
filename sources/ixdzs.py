# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://tw.m.ixdzs.com/search?k=%s'


class IxdzsCrawler(Crawler):

    base_url = ['https://tw.m.ixdzs.com/']


    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)
        results = []

        for data in soup.select('ul.ix-list.ix-border-t li div.ix-list-info.ix-border-t.burl'):
            title = data.select_one('h3 a').get_text().strip()
            url = self.absolute_url(
                data.select_one('h3 a')['href']
            )
            results.append(
                {
                    'title': title,
                    'url': url,
                }
            )
        return results
    # end def

    def read_novel_info(self):
            '''Get novel title, author, cover etc'''
            logger.debug('Visiting %s', self.novel_url)
            soup = self.get_soup(self.novel_url)

            self.novel_title = soup.select_one('header.ix-header.ix-border.ix-page h1').get_text()
            logger.info(f'Novel title: {self.novel_title}')

            self.novel_author = soup.select_one('div.ix-list-info.ui-border-t p').get_text()[3:]
            logger.info(f'Novel Author: {self.novel_author}')

            self.novel_cover = soup.select_one('div.ix-list-img-square img')['src']
            logger.info(f'Novel Cover: {self.novel_cover}')
            
            logger.info('Getting chapters...')
            for chapter in soup.select("ul.chapter li a"):       
                title = chapter.get_text()
                url = self.absolute_url(chapter['href'])

                chap_id = len(self.chapters) + 1
                if len(self.chapters) % 100 == 0:
                    vol_id = chap_id//100 + 1
                    vol_title = 'Volume ' + str(vol_id)
                    self.volumes.append({
                        'id': vol_id,
                        'title': vol_title
                    })

                self.chapters.append({
                    'id': chap_id,
                    'title': title,
                    'url': url,
                    'volume': vol_id
                })
    # end def

    def download_chapter_body(self, chapter):

        logger.info(f"Downloading {chapter['url']}")
        soup = self.get_soup(chapter['url'])

        content = soup.select("article.page-content section p")
        content = '\n'.join(str(p) for p in content)
        
        return content
    # end def
# end class
