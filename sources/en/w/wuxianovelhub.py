# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class MyCrawlerName(Crawler):

    base_url = [
        'https://www.wuxianovelhub.com/'
    ]
    has_manga = False
    machine_translation = False

    def initialize(self):
        pass
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def search_novel(self, query):
        pass
    # end def

    def read_novel_info(self):
        slug = re.findall(r'/novel/([^/]+)\.html', self.novel_url)[0]

        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)
        self.novel_title = soup.select_one('.novel-title').text
        logger.debug('Novel title = %s', self.novel_title)

        self.novel_author=soup.select_one("div.author").find_all('span')[-1].text
        logger.debug('Novel Author = %s', self.novel_author)
        # try:
        #     coverfigure=soup.select_one('.cover')
        #     self.novel_cover=self.absolute_url(coverfigure.find('img')['src'] )
        # except:
        #     pass
        # logger.info('Novel cover = %s', self.novel_cover)

        
        try:
            last_page=int(re.search(r'page=([0-9]+?)&',soup.select_one(".pagination-container").find_all('a', href=True)[-1]['href']).group(1))
            logger.debug(f'Last page of chapter is :{last_page}')
            self.volumes.append({'id': 1})
            i=0
            for page in range(0,last_page):
                logger.debug(f'Grabbing :{page}')
                page=self.get_soup(self.absolute_url(f'/e/extend/fy.php?page={page}&wjm={slug}'))
                for j in page.select_one(".chapter-list").find_all("li"):
                    self.chapters.append({
                        'id': i,
                        'volume': 1,
                        'url':  self.absolute_url(j.find_all('a', href=True)[0]['href']),
                        'title': j.select_one(".chapter-title").text
                    })
                    i+=1
                # end for
            # end for
        except:
            pass       

    # end def

    def download_chapter_body(self, chapter):

        soup=self.get_soup(chapter['url'])
        
        contents = self.cleaner.clean_contents(soup.find("div", class_="chapter-content"))

        return str(contents)
    # end def

    def get_chapter_index_of(self, url):
        pass
    # end def
# end class
