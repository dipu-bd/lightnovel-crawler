#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger('KISSLIGHTNOVEL')
search_url = 'https://kisslightnovels.info/?s=%s&post_type=wp-manga&author=&artist=&release='


class KissLightNovels(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h4 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one('.post-title h1')
        for badge in title_tag.select('.manga-title-badges'):
            badge.decompose()
        # end for
        self.novel_title = title_tag.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.summary_image a img')['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('.tab-summary .author-content a')
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else:
            self.novel_author = author[0].text
        # end if
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select('ul.main li.wp-manga-chapter a')
        chapters.reverse()

        volumes = set()
        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.text-left')

        if contents.select_one('#divReadContent'):
            chapter['title'] = contents.select_one('h4').text
            contents = contents.select_one('#divReadContent')
        # end if

        if contents.select_one('#snippet-box'):
            contents.select_one('#snippet-box').decompose()
        # end if

        if contents.h3:
            contents.h3.decompose()
        # end if

        for codeblock in contents.findAll('div', {'class': 'code-block'}):
            codeblock.decompose()
        # end for

        self.clean_contents(contents)
        return str(contents)
    # end def
# end class
