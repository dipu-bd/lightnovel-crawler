# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://asadatranslations.com/?s=%s&post_type=wp-manga&author=&artist=&release='


class AsadaTranslations(Crawler):
    base_url = 'https://asadatranslations.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h3 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })
        

        return results
    

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.post-title h1')
        for span in possible_title.select('span'):
            span.extract()
        
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover['content'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = ' '.join([
            a.text.strip()
            for a in soup.select('.author-content a[href*="manga-author"]')
        ])
        logger.info('%s', self.novel_author)

        volumes = set()
        chapters = soup.select('ul.main li.wp-manga-chapter a')
        for a in reversed(chapters):
            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        

        self.volumes = [{'id': x} for x in volumes]
    

    def initialize(self) -> None:
        self.cleaner.bad_css.update([
            'h3', '.code-block', '.adsbygoogle', '.sharedaddy'
        ])
        self.cleaner.blacklist_patterns.update([
            r'^Translator:',
            r'^Qii',
            r'^Editor:',
            r'^Maralynx',
            r'^Translator and Editor Notes:',
            r'^Support this novel on',
            r'^NU',
            r'^by submitting reviews and ratings or by adding it to your reading list.',
        ])
    

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.text-left')

        for discord in contents.select('p'):
            for bad in ["Join our", "<a>discord</a>", "to get latest updates and progress about the translations"]:
                if bad in discord.text:
                    discord.extract()

        return self.cleaner.extract_contents(contents)
    

