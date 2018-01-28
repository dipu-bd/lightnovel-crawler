#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main point of execution"""
import sys
from EbookCrawler.lnmtl import LNMTLCrawler
from EbookCrawler.wuxia import WuxiaCrawler


def main():
    '''main method to call'''
    if len(sys.argv) < 3:
        return show_help()
    # end if

    site = sys.argv[1]
    if site == 'wuxia':
        WuxiaCrawler(
            novel_id=sys.argv[2],
            start_url=sys.argv[3] if len(sys.argv) > 3 else None,
            end_url=sys.argv[4] if len(sys.argv) > 4 else None
        ).start()
    elif site == 'lnmtl':
        LNMTLCrawler(
            novel_id=sys.argv[2],
            start_url=sys.argv[3] if len(sys.argv) > 3 else '',
            end_url=sys.argv[4] if len(sys.argv) > 4 else ''
        ).start()
    else:
        show_help()
    # end if
# end def


def show_help():
    '''displays help'''
    print('EbookCrawler:')
    print('  python . <site-name> <novel-id>',
          '[<start-chapter>|<start-url>]',
          '[<end-chapter>|<end-url>]')
    print()
    print('OPTIONS:')
    print('site-name*   Site to crawl. Available: lnmtl, wuxia.')
    print('novel-id*    Novel id appear in url (See HINTS)')
    print('start-url    Url of the chapter to start')
    print('end-url      Url of the final chapter')
    print('end-chapter  Starting chapter')
    print('end-chapter  Ending chapter')
    print()
    print('HINTS:')
    print('- * marked params are required')
    print('- Do not provide any start or end chapter for just book binding')
    print('- Novel id of: `...wuxiaworld.com/desolate-era-index/de-...` is `desolate-era`')
    print('- Novel id of: `...lnmtl.../a-thought-through-eternity-chapter-573`',
          'is `a-thought-through-eternity`')
    print()
# end def

main()
