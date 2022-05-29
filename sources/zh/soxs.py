# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler


logger = logging.getLogger(__name__)
# search_url = 'https://tw.m.ixdzs.com/search?k=%s'


class Soxc(Crawler):

    base_url = ['https://www.soxs.cc/']


#     def search_novel(self, query):
#         query = query.lower().replace(' ', '+')
#         soup = self.get_soup(search_url % query)
#         results = []

#         for data in soup.select('.xiaoshuo h1'):
#             title = data.select_one('h3 a').get_text().strip()
#             url = self.absolute_url(
#                 data.select_one('h3 a')['href']
#             )
#             results.append(
#                 {
#                     'title': title,
#                     'url': url,
#                 }
#             )
#         return results
    # end def

    def read_novel_info(self):
        '''Get novel title, author, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        self.novel_url = self.novel_url.replace('/book/', '/')
        self.novel_url = self.novel_url.replace('.html', '/')
        soup = self.get_soup(self.novel_url)
        

        possible_title = soup.select_one('.xiaoshuo h1')
        assert possible_title, 'No novel title'
        self.novel_title =  possible_title.get_text()
        logger.info(f'Novel title: {self.novel_title}')

        self.novel_author = soup.select_one('.xiaoshuo h6').get_text()
        logger.info(f'Novel Author: {self.novel_author}')

        possible_novel_cover = soup.select_one('.book_cover img')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover['src'])
        logger.info(f'Novel Cover: {self.novel_cover}')
        
        logger.info('Getting chapters...')
        for chapter in soup.select(".novel_list dd a"):       
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
                #'title': title,
                'url': url,
                'volume': vol_id
            })
    # end def

    def download_chapter_body(self, chapter):

        logger.info(f"Downloading {chapter['url']}")

        soup = self.get_soup(chapter['url'])
        title = soup.select_one('.read_title h1').text.strip()
        chapter['title'] = title
        
        content = soup.select(".content")
        content = '\n'.join(str(p) for p in content)
        content = content.replace(self.novel_url, '')
        content = content.replace('soxscc', 'mtlrealm.com ')
        return content
    # end def
# end class
