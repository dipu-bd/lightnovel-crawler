# -*- coding: utf-8 -*-
import time
from typing import Dict, List
from urllib.parse import parse_qs, urlparse,urljoin
from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException



class NovelMTLTemplate(Crawler):
    # base_url = ['https://www.novelmtl.com/',#Check ok X
    #             'https://www.wuxiax.com/',#Check ok X
    #             'https://www.wuxiar.com/',#Check ok X
    #             'https://www.wuxiav.com/',#Check ok chapter title to check X
    #             'https://www.wuxiamtl.com/',#Check ok x
    #             'https://www.readwn.com/',#Check ok x
    #             'https://www.wuxianovelhub.com/',#Check ok x
    #             'https://www.ltnovel.com/',#Check ok X
    #             'https://www.novelmt.com/',#Check ok x
    #             ]
    is_template = True


    def initialize(self) -> None:
        self.cur_time = int(1000 * time.time())
    # end def

    def search_novel(self, query)-> Dict[str, str] :
        '''Search for a novel and return the search results.'''
        result = []
        search_url=self.absolute_url('/search.html')
        soup = self.get_soup(search_url)
        form = soup.select_one('.search-container form[method="post"]')
        if not form:
            pass
        # end if

        payload = {}
        url = urljoin(mirror,form['action'])
        for input in form.select('input'):
            payload[input['name']] = input['value']
        # end for
        payload['keyboard'] = query

        soup = self.post_soup(url, data=payload, headers={
            'Referer': search_url,
            'Origin': f'{mirror}',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        
        
        for a in soup.select('ul.novel-list .novel-item a')[:10]:
            for i in a.select('.material-icons'):
                i.extract()
            # end for
            result.append({
                'url': urljoin(mirror,a['href']),
                'title': a.select_one('.novel-title').text.strip(),
                'info': ' | '.join([x.text.strip() for x in a.select('.novel-stats')]),
            })
            #end for
        return result
    # end def

    def read_novel_info(self) -> None:
        chapter_list_url =self.absolute_url('/e/extend/fy.php')
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.novel-info .novel-title')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('#novel figure.cover img')['data-src'])
        except Exception as e:
             LNException('Failed to get novel cover: %s', e)

        try:
            self.novel_author = soup.select_one(
                '.novel-info .author span[itemprop="author"]').text.strip()
        except Exception as e:
            LNException('Failed to parse novel author. Error: %s', e)

        last_page = soup.select('#chapters .pagination li a')[-1]['href']

        last_page_qs = parse_qs(urlparse(last_page).query)
        max_page = int(last_page_qs['page'][0])
        wjm = last_page_qs['wjm'][0]

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

    def download_chapter_body(self, chapter)-> None:
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.chapter-content')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
