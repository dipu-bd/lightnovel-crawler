#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .anythingnovel import AnythingNovelCrawler
from .babelnovel import BabelNovelCrawler
from .bestlightnovel import BestLightNovel
from .boxnovel import BoxNovelCrawler
from .chinesefantasy import ChineseFantasyNovels
from .comrademao import ComrademaoCrawler
from .creativenovels import CreativeNovelsCrawler
from .crescentmoon import CrescentMoonCrawler
from .fourscanlation import FourScanlationCrawler
from .fullnovellive import FullnovelLiveCrawler
from .gravitytales import GravityTalesCrawler
from .idqidian import IdqidianCrawler
from .litnet import LitnetCrawler
from .lnmtl import LNMTLCrawler
from .machinetrans import MachineNovelTrans
from .meionovel import MeionovelCrawler
from .mtlednovels import MtledNovelsCrawler
from .myoniyonitrans import MyOniyOniTranslation
from .novelall import NovelAllCrawler
from .novelfull import NovelFullCrawler
from .novelgo import NovelGoCrawler
from .novelplanet import NovelPlanetCrawler
from .novelspread import NovelSpreadCrawler
from .noveluniverse import NovelUniverseCrawler
from .novelv import NovelvCrawler
from .readln import ReadLightNovelCrawler
from .readnovelfull import ReadNovelFullCrawler
from .rebirthonline import RebirthOnlineCrawler
from .romanticlb import RomanticLBCrawler
from .royalroad import RoyalRoadCrawler
from .scribblehub import ScribbleHubCrawler
from .tapread import TapreadCrawler
from .volarenovels import VolareNovelsCrawler
from .wattpad import WattpadCrawler
from .webnonline import WebnovelOnlineCrawler
from .webnovel import WebnovelCrawler
from .worldnovelonline import WorldnovelonlineCrawler
from .wuxiaco import WuxiaCoCrawler
from .wuxiacom import WuxiaComCrawler
from .wuxiaonline import WuxiaOnlineCrawler
from .yukinovel import YukiNovelCrawler
from .zenithnovels import ZenithNovelsCrawler
from .novelraw import NovelRawCrawler
from .lightnovelonline import LightNovelOnline

crawler_list = {
    # Do not forget to append a slash(/) at the end of the url
    'http://gravitytales.com/': GravityTalesCrawler,
    'http://novelfull.com/': NovelFullCrawler,
    'http://www.machinenoveltranslation.com/': MachineNovelTrans,
    'http://zenithnovels.com/': ZenithNovelsCrawler,
    'https://anythingnovel.com/': AnythingNovelCrawler,
    'https://babelnovel.com/': BabelNovelCrawler,
    'https://bestlightnovel.com/': BestLightNovel,
    'https://boxnovel.com/': BoxNovelCrawler,
    'https://creativenovels.com/': CreativeNovelsCrawler,
    'https://crescentmoon.blog/': CrescentMoonCrawler,
    'https://light-novel.online/': LightNovelOnline,
    'https://litnet.com/': LitnetCrawler,
    'https://lnmtl.com/': LNMTLCrawler,
    'https://m.chinesefantasynovels.com/': ChineseFantasyNovels,
    'https://m.novelspread.com/': NovelSpreadCrawler,
    'https://m.romanticlovebooks.com/': RomanticLBCrawler,
    'https://m.wuxiaworld.co/': WuxiaCoCrawler,
    'https://meionovel.com/': MeionovelCrawler,
    'https://mtled-novels.com/': MtledNovelsCrawler,
    'https://myoniyonitranslations.com/': MyOniyOniTranslation,
    'https://novelgo.id/': NovelGoCrawler,
    'https://novelplanet.com/': NovelPlanetCrawler,
    'https://novelraw.blogspot.com/': NovelRawCrawler,
    'https://readnovelfull.com/': ReadNovelFullCrawler,
    'https://webnovel.online/': WebnovelOnlineCrawler,
    'https://wuxiaworld.online/': WuxiaOnlineCrawler,
    'https://www.idqidian.us/': IdqidianCrawler,
    'https://www.novelall.com/': NovelAllCrawler,
    'https://www.novelspread.com/': NovelSpreadCrawler,
    'https://www.readlightnovel.org/': ReadLightNovelCrawler,
    'https://www.rebirth.online/': RebirthOnlineCrawler,
    'https://www.romanticlovebooks.com/': RomanticLBCrawler,
    'https://www.royalroad.com/': RoyalRoadCrawler,
    'https://www.scribblehub.com/': ScribbleHubCrawler,
    'https://www.tapread.com/': TapreadCrawler,
    'https://www.volarenovels.com/': VolareNovelsCrawler,
    'https://www.wattpad.com/': WattpadCrawler,
    'https://www.webnovel.com/': WebnovelCrawler,
    'https://www.worldnovel.online/': WorldnovelonlineCrawler,
    'https://www.wuxiaworld.co/': WuxiaCoCrawler,
    'https://www.wuxiaworld.com/': WuxiaComCrawler,
    'https://yukinovel.id/': YukiNovelCrawler,
    # 'http://fullnovel.live/': FullnovelLiveCrawler,
    # 'https://comrademao.com/': ComrademaoCrawler,
    # 'https://4scanlation.xyz/': FourScanlationCrawler,
    # 'https://www.noveluniverse.com/': NovelUniverseCrawler,
    # 'https://www.novelv.com/': NovelvCrawler,
    # Do not forget to append a slash(/) at the end of the url
}
