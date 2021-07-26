# -*- coding: utf-8 -*-
import logging
import re
from concurrent import futures
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'http://boxnovel.cloud/search?keyword=%s'


class BoxNovelCloud(Crawler):
    base_url = 'http://boxnovel.cloud/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.col-novel-main .list-novel .row'):
            search_title = tab.select_one('.novel-title a')
            latest = tab.select_one('.text-info a').text.strip()
            results.append({
                'title': search_title.text.strip(),
                'url': self.absolute_url(
                    tab.select_one('.novel-title a')['href']),
                'info': 'Latest chapter: %s' % (latest)
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = ' '.join([
            str(x)
            for x in soup.select_one('.title').contents
            if not x.name
        ]).strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.book img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.find_all(href=re.compile('author'))
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else:
            self.novel_author = author[0].text
        logger.info('Novel author: %s', self.novel_author)

        # This is copied from the Novelfull pagination 'hanlder' with minor tweaks
        pagination_links = soup.select('.pagination li a')
        pagination_page_numbers = []
        for pagination_link in pagination_links:
            # Boxnovel.org pagination numbering boxes contain non-digit characters
            if pagination_link.text.isdigit():
                pagination_page_numbers.append(int(pagination_link.text))

        page_count = max(
            pagination_page_numbers) if pagination_page_numbers else 0
        logger.info('Chapter list pages: %d' % page_count)

        logger.info('Getting chapters...')
        futures_to_check = {
            self.executor.submit(
                self.download_chapter_list,
                i + 1,
            ): str(i)
            for i in range(page_count + 1)
        }
        [x.result() for x in futures.as_completed(futures_to_check)]

        # Didn't test without this, but with pagination the chapters could be in different orders
        logger.info('Sorting chapters...')
        self.chapters.sort(key=lambda x: x['volume'] * 1000 + x['id'])

        # Copied straight from Novelfull
        logger.info('Adding volumes...')
        mini = self.chapters[0]['volume']
        maxi = self.chapters[-1]['volume']
        for i in range(mini, maxi + 1):
            self.volumes.append({'id': i})
        # end for
    # end def

    def download_chapter_list(self, page):
        '''Download list of chapters and volumes.'''
        url = self.novel_url.split('?')[0].strip('/')
        url += '?page=%d&per-page=50' % page
        soup = self.get_soup(url)

        for a in soup.select('ul.list-chapter li a'):
            title = a['title'].strip()

            chapter_id = len(self.chapters) + 1
            # match = re.findall(r'ch(apter)? (\d+)', title, re.IGNORECASE)
            # if len(match) == 1:
            #     chapter_id = int(match[0][1])
            # # end if

            volume_id = 1 + (chapter_id - 1) // 100
            match = re.findall(r'(book|vol|volume) (\d+)',
                               title, re.IGNORECASE)
            if len(match) == 1:
                volume_id = int(match[0][1])
            # end if

            data = {
                'title': title,
                'id': chapter_id,
                'volume': volume_id,
                'url': self.absolute_url(a['href']),
            }
            self.chapters.append(data)
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.chr-c, #chr-content')
        return self.extract_contents(contents)
    # end def
# end class