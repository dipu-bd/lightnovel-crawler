#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .lnmtl import LNMTLCrawler
from .webnovel import WebnovelCrawler
from .wuxiacom import WuxiaComCrawler
from .wuxiaco import WuxiaCoCrawler
from .wuxiaonline import WuxiaOnlineCrawler
from .boxnovel import BoxNovelCrawler
from .readln import ReadLightNovelCrawler
from .novelplanet import NovelPlanetCrawler
from .lnindo import LnindoCrawler
from .idqidian import IdqidianCrawler
from .romanticlb import RomanticLBCrawler
from .webnonline import WebnovelOnlineCrawler
from .fullnovellive import FullnovelLiveCrawler
from .novelall import NovelAllCrawler
from .novelfull import NovelFullCrawler
from .novelspread import NovelSpreadCrawler
from .gravitytales import GravityTalesCrawler
from .machinetrans import MachineNovelTrans
from .novelonlinefree import NovelOnlineFreeCrawler
from .anythingnovel import AnythingNovelCrawler
from .royalroad import RoyalRoadCrawler
from .comrademao import ComrademaoCrawler
from .chinesefantasy import ChineseFantasyNovels
from .scribblehub import ScribbleHubCrawler
from .zenithnovels import ZenithNovelsCrawler
from .noveluniverse import NovelUniverseCrawler
from .meionovel import MeionovelCrawler

crawler_list = {
    # Do not forget to append a slash(/) at the end of the url
    'https://lnmtl.com/': LNMTLCrawler,
    'https://www.webnovel.com/': WebnovelCrawler,
    'https://webnovel.online/': WebnovelOnlineCrawler,
    'https://wuxiaworld.online/': WuxiaOnlineCrawler,
    'https://www.wuxiaworld.com/': WuxiaComCrawler,
    'https://www.wuxiaworld.co/': WuxiaCoCrawler,
    'https://m.wuxiaworld.co/': WuxiaCoCrawler,
    'https://boxnovel.com/': BoxNovelCrawler,
    'https://novelplanet.com/': NovelPlanetCrawler,
    'https://www.readlightnovel.org/': ReadLightNovelCrawler,
    'https://lnindo.org/': LnindoCrawler,
    'https://www.idqidian.us/': IdqidianCrawler,
    'https://m.romanticlovebooks.com/': RomanticLBCrawler,
    'https://www.romanticlovebooks.com/': RomanticLBCrawler,
    'http://fullnovel.live/': FullnovelLiveCrawler,
    'https://www.novelall.com/': NovelAllCrawler,
    'http://novelfull.com/': NovelFullCrawler,
    'https://m.novelspread.com/': NovelSpreadCrawler,
    'https://www.novelspread.com/': NovelSpreadCrawler,
    'http://gravitytales.com/': GravityTalesCrawler,
    'http://www.machinenoveltranslation.com/': MachineNovelTrans,
    'https://novelonlinefree.info/': NovelOnlineFreeCrawler,
    'https://anythingnovel.com/': AnythingNovelCrawler,
    'https://www.royalroad.com/': RoyalRoadCrawler,
    'https://comrademao.com/': ComrademaoCrawler,
    'https://m.chinesefantasynovels.com/': ChineseFantasyNovels,
    'https://www.scribblehub.com/': ScribbleHubCrawler,
    'http://zenithnovels.com/': ZenithNovelsCrawler,
    'https://www.noveluniverse.com/': NovelUniverseCrawler,
    'https://meionovel.com/': MeionovelCrawler,
    # Do not forget to append a slash(/) at the end of the url
}
