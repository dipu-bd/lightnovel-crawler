# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

SEARCH_URL = 'https://www.mtlreader.com/search'
CHAPTER_DETAIL_API = 'https://www.mtlreader.com/api/chapter-content/%s'


class MtlReaderCrawler(Crawler):
    machine_translation = True
    base_url = [
        'https://www.mtlreader.com/',
    ]

    def search_novel(self, query):
        logger.debug('Visiting: %s', self.home_url)
        soup = self.get_soup(self.home_url)
        logger.debug(soup.select('form[action="%s"] input' % SEARCH_URL))

        form_data = {}
        for input in soup.select('form[action="%s"] input' % SEARCH_URL):
            form_data[input['name']] = input.get('value', '')
        # end for
        form_data['input'] = quote(query)

        logger.debug('Form data: %s', form_data)
        response = self.submit_form(SEARCH_URL, form_data)
        soup = self.make_soup(response)

        results = []
        for div in soup.select('.property_item .proerty_text'):
            a = div.select_one('a')
            info = div.select_one('p.text-muted, p')
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': info.text.strip() if info else '',
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.our-agent-box h3').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('meta[property="og:image"]')['content'])
        except Exception as e:
            logger.debug('Could not find novel cover. Error %s', e)
        logger.info('Novel cover: %s', self.novel_cover)

        try:
            possible_author = soup.select_one('.agent-p-contact .fa.fa-user')
            self.novel_author = possible_author.parent.text.strip()
            self.novel_author = re.sub(r'Author[: ]+', '', self.novel_author)
        except Exception as e:
            logger.debug('Could not find novel author. Error %s', e)
        logger.info('Novel author: %s', self.novel_author)

        for a in soup.select('table td a[href*="/chapters/"]'):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})
            # end if
            chap_title = re.sub(r'^(\d+[\s:\-]+)', '', a.text.strip())
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': chap_title,
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        self.get_response(chapter['url'])

        xsrf_token = self.cookies.get('XSRF-TOKEN')
        logger.debug('XSRF Token: %s', xsrf_token)

        chapter_id = re.findall(r'/chapters/(\d+)', chapter['url'])[0]
        url = CHAPTER_DETAIL_API % chapter_id
        logger.debug('Visiting: %s', url)

        response = self.get_response(url, headers={
            'referer': chapter['url'],
            'x-xsrf-token': xsrf_token,
            'accept': 'application/json, text/plain, */*',
        })
        # soup = self.make_soup(response.json())
        # return self.extract_contents(soup.select_one('body'))
        text = re.sub('([\r\n]?<br>[\r\n]?)+', '\n\n', response.json())
        return '\n'.join(['<p>' + x.strip() + '</p>' for x in text.split('\n\n')])
    # end def
# end class
