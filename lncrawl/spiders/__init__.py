#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .anythingnovel import AnythingNovelCrawler
from .boxnovel import BoxNovelCrawler
from .chinesefantasy import ChineseFantasyNovels
from .comrademao import ComrademaoCrawler
from .crescentmoon import CrescentMoonCrawler
from .fullnovellive import FullnovelLiveCrawler
from .gravitytales import GravityTalesCrawler
from .idqidian import IdqidianCrawler
from .litnet import LitnetCrawler
from .lnindo import LnindoCrawler
from .lnmtl import LNMTLCrawler
from .machinetrans import MachineNovelTrans
from .meionovel import MeionovelCrawler
from .mtlednovels import MtledNovelsCrawler
from .novelall import NovelAllCrawler
from .novelfull import NovelFullCrawler
from .novelonlinefree import NovelOnlineFreeCrawler
from .novelplanet import NovelPlanetCrawler
from .novelspread import NovelSpreadCrawler
from .noveluniverse import NovelUniverseCrawler
from .novelv import NovelvCrawler
from .readln import ReadLightNovelCrawler
from .romanticlb import RomanticLBCrawler
from .royalroad import RoyalRoadCrawler
from .scribblehub import ScribbleHubCrawler
from .volarenovels import VolareNovelsCrawler
from .webnonline import WebnovelOnlineCrawler
from .webnovel import WebnovelCrawler
from .worldnovelonline import WorldnovelonlineCrawler
from .wuxiaco import WuxiaCoCrawler
from .wuxiacom import WuxiaComCrawler
from .wuxiaonline import WuxiaOnlineCrawler
from .zenithnovels import ZenithNovelsCrawler

crawler_list = {
    # Do not forget to append a slash(/) at the end of the url
    'http://fullnovel.live/': FullnovelLiveCrawler,
    'http://gravitytales.com/': GravityTalesCrawler,
    'http://novelfull.com/': NovelFullCrawler,
    'http://www.machinenoveltranslation.com/': MachineNovelTrans,
    'http://zenithnovels.com/': ZenithNovelsCrawler,
    'https://anythingnovel.com/': AnythingNovelCrawler,
    'https://boxnovel.com/': BoxNovelCrawler,
    'https://comrademao.com/': ComrademaoCrawler,
    'https://crescentmoon.blog/': CrescentMoonCrawler,
    'https://litnet.com/': LitnetCrawler,
    'https://lnindo.org/': LnindoCrawler,
    'https://lnmtl.com/': LNMTLCrawler,
    'https://m.chinesefantasynovels.com/': ChineseFantasyNovels,
    'https://m.novelspread.com/': NovelSpreadCrawler,
    'https://m.romanticlovebooks.com/': RomanticLBCrawler,
    'https://m.wuxiaworld.co/': WuxiaCoCrawler,
    'https://meionovel.com/': MeionovelCrawler,
    'https://mtled-novels.com/': MtledNovelsCrawler,
    'https://novelonlinefree.info/': NovelOnlineFreeCrawler,
    'https://novelplanet.com/': NovelPlanetCrawler,
    'https://volarenovels.com/': VolareNovelsCrawler,
    'https://webnovel.online/': WebnovelOnlineCrawler,
    'https://wuxiaworld.online/': WuxiaOnlineCrawler,
    'https://www.idqidian.us/': IdqidianCrawler,
    'https://www.novelall.com/': NovelAllCrawler,
    'https://www.novelspread.com/': NovelSpreadCrawler,
    'https://www.noveluniverse.com/': NovelUniverseCrawler,
    'https://www.novelv.com/': NovelvCrawler,
    'https://www.readlightnovel.org/': ReadLightNovelCrawler,
    'https://www.romanticlovebooks.com/': RomanticLBCrawler,
    'https://www.royalroad.com/': RoyalRoadCrawler,
    'https://www.scribblehub.com/': ScribbleHubCrawler,
    'https://www.webnovel.com/': WebnovelCrawler,
    'https://www.worldnovel.online/': WorldnovelonlineCrawler,
    'https://www.wuxiaworld.co/': WuxiaCoCrawler,
    'https://www.wuxiaworld.com/': WuxiaComCrawler,
    # Do not forget to append a slash(/) at the end of the url
}
