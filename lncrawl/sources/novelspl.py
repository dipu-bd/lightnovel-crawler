# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.novels.pl/?search=%s'
chapter_list_url = 'https://www.novels.pl/ajax/ajaxGetChapters.php'


class NovelsPlCrawler(Crawler):
    base_url = [
        'https://novels.pl/',
        'https://www.novels.pl/'
    ]

    def initialize(self):
        self.home_url = 'https://www.novels.pl/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('#table a'):
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '',
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        title = soup.select_one('h4.panel-title').text
        self.novel_title = title.rsplit('|')[0].strip()
        logger.debug('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(soup.select_one('.imageCover img.img-thumbnail')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one('.panel-body .coll a[href^="/author/"]').text
        logger.info('Novel author: %s', self.novel_author)

        novel_id = None
        novel_hash = None
        chapter_count = None
        total_pages = None
        for script in soup.select('.panel-group script'):
            data = re.findall(r"data: \{id:(\d+), novel:'([^']+)', max:(\d+), page: page\}", str(script))
            if not data:
                continue
            # end if
            data = data[0]
            novel_id = int(data[0])
            novel_hash = data[1]
            chapter_count = int(data[2])
            logger.info('Novel id: %d', novel_id)
            logger.info('Novel hash: %s', novel_hash)
            logger.info('Chapter count: %d', chapter_count)
            data = re.findall(r'totalPages: (\d+)', str(script))
            total_pages = int(data[0])
            logger.info('Total pages: %d', total_pages)
        # end for
        if not (novel_id and total_pages):
            raise Exception('Could not find novel id')
        # end if

        futures = {}
        for page in range(1, total_pages + 1):
            f = self.executor.submit(
                self.submit_form,
                chapter_list_url,
                data={
                    'id': novel_id,
                    'novel': novel_hash,
                    'max': chapter_count,
                    'page': page,
                }
            )
            futures[page] = f
        # end for
        
        volumes = set([])
        for page in reversed(range(1, total_pages + 1)):
            soup = self.make_soup(futures[page].result())
            for tr in reversed(soup.select('tr')):
                chap_id = int(tr.select('td')[0].text)
                vol_id = 1 + chap_id // 100
                volumes.add(vol_id)
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': tr.select_one('a').text,
                    'url': self.absolute_url(tr.select_one('a')['href']),
                })
            # end for
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select('.panel-body.article p')
        return ''.join([str(p) for p in contents])
    # end def
# end class
