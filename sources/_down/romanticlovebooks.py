# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

ajaxchapter_url = 'https://www.romanticlovebooks.com/home/index/ajaxchapter'


class RomanticLBCrawler(Crawler):
    base_url = [
        'https://m.romanticlovebooks.com/',
        'https://www.romanticlovebooks.com/',
    ]

    def initialize(self):
        self.home_url = 'https://www.romanticlovebooks.com/'
    

    def read_novel_info(self):
        url = self.novel_url.replace(
            'https://m.romanticlovebooks', 'https://www.romanticlovebooks')
        soup = self.get_soup(url)

        possible_title = soup.select_one('body > div > div.rt > h1')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        possible_image = soup.select_one('body > div > div.lf > img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])

        for info in soup.select('body > div > div.msg > *'):
            text = info.text.strip()
            if text.lower().startswith('author'):
                self.novel_author = text
                break

        

        chap_id = 0
        for a in soup.select('body > div.mulu ul')[-1].select('li a'):
            vol_id = chap_id // 100 + 1
            if vol_id > len(self.volumes):
                self.volumes.append({
                    'id': vol_id,
                    'title': 'Volume %d' % vol_id
                })


            chap_id += 1
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'],
                'url': self.absolute_url(a['href']),
            })
        
    

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('#content')
        return self.cleaner.extract_contents(contents)
    

    # def download_chapter_body(self, chapter):
    #     '''Download body of a single chapter and return as clean html format.'''
    #     logger.info('Visiting %s', chapter['url'])
    #     soup = self.get_soup(chapter['url'])

    #     urlcontent = dict()
    #     for script in soup.select('head script'):
    #         content = re.findall('var ([a-z_]+) = \"([^"]+)\";', script.text)
    #         if not len(content):
    #             continue

    #         data = {x[0]: x[1] for x in content}
    #         urlcontent = dict(
    #             id=data.get('article_id', ''),
    #             eKey=data.get('hash', ''),
    #             cid=data.get('chapter_id', ''),
    #             basecid=data.get('chapter_id', '')
    #         )
    #         chapter['title'] = data.get('chaptername', chapter['title'])
    #         break
    #     

    #     contents = soup.select_one('#BookText')
    #     body = self.cleaner.extract_contents(contents)
    #     if len(body) > 2 or body[0].strip() != 'Loading...':
    #         return '<p>' + '</p><p>'.join(body) + '</p>'


    #     r = self.submit_form(ajaxchapter_url, data=urlcontent)
    #     data = r.json()

    #     soup = BeautifulSoup(data['info']['content'], 'lxml')
    #     contents = soup.select_one('body')
    #     body = self.cleaner.extract_contents(contents)
    #     return '<p>' + '</p><p>'.join(body) + '</p>'
    # 

