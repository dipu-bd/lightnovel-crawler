# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from hashlib import md5
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class FlyingLinesCrawler(Crawler):
    base_url = 'https://www.flying-lines.com/'

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.novel-info .title h2').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.novel .novel-thumb img')['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        authors = [x.text.strip()
                   for x in soup.select('.novel-info ul.profile li')]
        self.novel_author = ', '.join(authors)
        logger.info('%s', self.novel_author)

        self.novel_id = urlparse(self.novel_url).path.split('/')[2]
        logger.info("Novel id: %s", self.novel_id)

        for a in soup.select('ul.volume-chapters li a'):
            chap_id = int(a['data-chapter-number'])
            vol_id = 1 + (chap_id - 1) // 100
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url':  self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        # How to get the key?
        # - check `app.js` (Sources/cdn.flying-lines.com/front/../js/app.js)
        # - locate the mapped value of `./what` (e.g.: "./what": 57,)
        # - locate the mapped valued function. (e.g: search `57:`)
        # - Copy key from the function. (return "4ec781a70c3f11ea9b46f23c918347ac")
        key = '4ec781a70c3f11ea9b46f23c918347ac'

        # How to find the sign generation method?
        # - check `app.js`
        # - search the mapped value of `./nobody`
        # - locate the mapped valued function. (e.g: search `48:`)
        time = str(int(datetime.now().timestamp() * 1000))
        sign = 'chapterNum=%s&novelPath=%s&time=%s&webdriver=0&key=%s' % (
            chapter['id'], self.novel_id, time, key)
        sign = md5(sign.encode('utf8')).hexdigest()

        # How to generate the URL?
        # - check `app.js`
        # - search for `e.data.meta`
        url = '%s/h5/novel/%s/%s?accessToken=&isFirstEnter=1&webdriver=0&time=%s&sign=%s'
        url = url % (self.base_url.strip('/'), self.novel_id, chapter['id'], time, sign)

        logger.info('Downloading %s', url)
        data = self.post_json(url, headers={
            'Origin': self.base_url.strip('/'),
            'Referer': self.base_url.strip('/') + '/novel/' + self.novel_id,
        })

        # How to find the decryption method?
        # - check `app.js`
        # - search for `TurnCharIntoString:` function
        encrypted = data['data']['content']
        n = data['data']['nowTime']
        even_shift = int(n[-1])
        odd_shift = int(n[-2])
        content = ''
        for i, ch in enumerate(encrypted):
            if i % 2 == 0:
                content += chr(ord(ch) - even_shift)
            else:
                content += chr(ord(ch) - odd_shift)
        return content
    # end def
# end class
