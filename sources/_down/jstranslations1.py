# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class JSTranslations(Crawler):
    base_url = 'https://jstranslations1.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.entry-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = "Translated by JS Translations"
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('figure.wp-block-image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        # TODO: There are some novels on site that use different layout, need to find a way to check for both.
        chapters = soup.select(
            'div.wp-block-coblocks-accordion-item__content ul li a')

        for a in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('.entry-content')

        # TODO: Refactor below code to make it simpler but still remove all junk text.
        # Removes junk text in chapter body
        for content in body_parts.select("p"):
            for bad in ["[TL Note:", "! I’ll post bonus chapters!]", "There’s a", "for terms left in pinyin in the menu above, for those who need it!"]:
                if bad in content.text:
                    content.extract()
                # end if
        # end for

        # Removes junk text in bold
        for content in body_parts.select("p strong"):
            for bad in ["NEXT", "BACK", "This site runs on ads, so please turn off your Ad-Blocker to support your translator!", "***[There’s a glossary now for terms left in pinyin in the above menu, for those who need it!]", "supporting me. Buy me a coffee!", "***[", "GLOSSARY", "ALL AVAILABLE CHAPTERS ARE LISTED ON THE TABLE OF CONTENTS PAGE UNDER CURRENT [BG] ROMANCE PROJECTS!]", "A kind reader bought me a", "! Thank you very much for your support! Here is the promised bonus chapter! ❤", "|| TABLE OF CONTENTS ||"]:
                if bad in content.text:
                    content.extract()
                # end if
        # end for

        # Removes junk text in span
        for content in body_parts.select("p span"):
            for bad in ["happy holidays to you and your loved ones!"]:
                if bad in content.text:
                    content.extract()
                # end if
        # end for

        # Removes junk links
        for content in body_parts.select("p a"):
            for bad in ["supporting me. Buy me a coffee", "coffee"]:
                if bad in content.text:
                    content.extract()
                # end if
        # end for

        # Removes junk text in ul tags
        for content in body_parts.select("ul"):
            for bad in ["THIS SITE RUNS ON ADS, SO PLEASE TURN OFF YOUR AD-BLOCKER TO SUPPORT YOUR TRANSLATOR!A GLOSSARY IS HERE for terms left in pinyin, for those who need it!ALL AVAILABLE CHAPTERS ARE LISTED ON THE TABLE OF CONTENTS PAGE UNDER CURRENT [BG] ROMANCE PROJECTS!]", "Want to read more? BUY ME A COFFEE for bonus chapters/ parts!Want to read even MORE? Consider BECOMING A PATRON for monthly access to rough drafts of advanced chapters!Or you can support my work by DONATING DIRECTLY THROUGH PAYPAL!Thank you for your support! ❤", "Want to read more? BUY ME A COFFEE for bonus chapters / parts!Want to read even MORE? Consider BECOMING A PATRON for monthly access to rough drafts of advanced chapters!Or you can support my work by DONATING DIRECTLY THROUGH PAYPAL!Thank you for your support! ❤"]:
                if bad in content.text:
                    content.extract()
                # end if
        # end for

        # Removes share button
        for share in body_parts.select('h3.sd-title'):
            share.extract()
        # end for

        # Removes like button
        for like in body_parts.select('span.button'):
            like.extract()
        # end for

        # Removes loading text left behind by comments
        for comments in body_parts.select('span.loading'):
            comments.extract()
        # end for

        # Removes double spacing.
        
        # end for

        return self.extract_contents(body_parts)
    # end def
# end class
