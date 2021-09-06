# -*- coding: utf-8 -*-
import logging
import time
from urllib.parse import parse_qs, urlparse
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://www.novelmtl.com/search.html'
chapter_list_url = 'https://www.novelmtl.com/e/extend/fy.php'


class NovelMTLCrawler(Crawler):
    base_url = 'https://www.novelmtl.com/'

    def initialize(self) -> None:
        self.cur_time = int(1000 * time.time())
    # end def

    def search_novel(self, query):
        '''Search for a novel and return the search results.'''
        soup = self.get_soup(search_url)
        form = soup.select_one('.search-container form[method="post"]')
        if not form:
            return []
        # end if

        payload = {}
        url = self.absolute_url(form['action'])
        for input in form.select('input'):
            payload[input['name']] = input['value']
        # end for
        payload['keyboard'] = query

        soup = self.post_soup(url, data=payload, headers={
            'Referer': search_url,
            'Origin': 'https://www.novelmtl.com',
            'Content-Type': 'application/x-www-form-urlencoded',
        })

        result = []
        for a in soup.select('ul.novel-list .novel-item a')[:10]:
            for i in a.select('.material-icons'):
                i.extract()
            # end for
            result.append({
                'url': self.absolute_url(a['href']),
                'title': a.select_one('.novel-title').text.strip(),
                'info': ' | '.join([x.text.strip() for x in a.select('.novel-stats')]),
            })
        # end for
        return result
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.novel-info .novel-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('#novel figure.cover img')['data-src'])
            logger.info('Novel cover: %s', self.novel_cover)
        except Exception as e:
            logger.debug('Failed to get novel cover: %s', e)

        try:
            self.novel_author = soup.select_one(
                '.novel-info .author span[itemprop="author"]').text.strip()
            logger.info('%s', self.novel_author)
        except Exception as e:
            logger.debug('Failed to parse novel author. Error: %s', e)

        last_page = soup.select('#chapters .pagination li a')[-1]['href']
        logger.debug('Last page: %s', last_page)

        last_page_qs = parse_qs(urlparse(last_page).query)
        max_page = int(last_page_qs['page'][0])
        wjm = last_page_qs['wjm'][0]
        logger.debug('Max page: %d, wjm = %s', max_page, wjm)

        futures = []
        for i in range(max_page + 1):
            payload = {
                'page': i,
                'wjm': wjm,
                '_': self.cur_time,
                'X-Requested-With': 'XMLHttpRequest',
            }
            url = chapter_list_url + '?' + '&'.join([
                '%s=%s' % (k, v) for k, v in payload.items()
            ])
            logger.debug('Fetching chapters from %s', url)
            futures.append(self.executor.submit(self.get_soup, url))
        # end for

        for page, f in enumerate(futures):
            soup = f.result()
            vol_id = page + 1
            self.volumes.append({'id': vol_id})
            for a in soup.select('ul.chapter-list li a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url': self.absolute_url(a['href']),
                    'title': a.select_one('.chapter-title').text.strip(),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.chapter-content')
        return self.extract_contents(contents)
    # end def
# end class
