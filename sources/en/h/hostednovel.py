# -*- coding: utf-8 -*-
import logging
import re
from bs4 import BeautifulSoup
from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class HostedNovelCom(Crawler):
    base_url = 'https://hostednovel.com/'

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_image = soup.select_one('.card-body img.cover-image')
        assert isinstance(possible_image, Tag)

        self.novel_title = possible_image['alt']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for p in soup.select('.card-body p'):
            if 'written by' in p.text.lower():
                author = re.sub(r'written by:?', '', p.text, flags=re.I + re.M)
                author = re.sub(r'\([^\u0000-\u007f]+\)', '', author)
                self.novel_author = author.strip()
                break
        # end for
        logger.info('Novel author: %s', self.novel_author)

        xsrf_token = self.cookies['XSRF-TOKEN']

        futures = {}
        for div in soup.select('.chaptergroups .chaptergroup'):
            vol_id = 1 + len(self.volumes)
            possible_title = div.select_one('.card-header h3')
            if isinstance(possible_title, Tag):
                vol_title = possible_title.text
            else:
                vol_title = f'Volume {vol_id}'
            # end if
            self.volumes.append({
                'id': vol_id,
                'title': vol_title
            })

            data_id = str(div['data-id'])
            url = self.novel_url.strip('/') + '/chapters/' + data_id
            f = self.executor.submit(self.get_soup, url, headers={
                'x-xsrf-token': xsrf_token,
                'referer': self.novel_url,
                'accept': 'application/json, text/plain, */*',
            })
            futures[vol_id] = f
        # end for

        for vol_id, f in sorted(futures.items()):
            soup = f.result()
            assert isinstance(soup, BeautifulSoup)
            for a in soup.select('.table-row a'):
                chap_id = 1 + len(self.chapters)
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href'])
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('#chapter')
        return self.extract_contents(content)
    # end def
# end class
