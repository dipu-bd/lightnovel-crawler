#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .anythingnovel import AnythingNovelCrawler
from .asianhobbyist import AsianHobbyistCrawler
from .babelnovel import BabelNovelCrawler
from .bestlightnovel import BestLightNovel
from .boxnovel import BoxNovelCrawler
from .chinesefantasy import ChineseFantasyNovels
from .comrademao import ComrademaoCrawler
from .creativenovels import CreativeNovelsCrawler
from .crescentmoon import CrescentMoonCrawler
from .fanfiction import FanFictionCrawler
from .fourscanlation import FourScanlationCrawler
from .fullnovellive import FullnovelLiveCrawler
from .gravitytales import GravityTalesCrawler
from .idqidian import IdqidianCrawler
from .jieruihao import JieruihaoCrawler
from .kisslightnovels import KissLightNovels
from .lightnovelonline import LightNovelOnline
from .litnet import LitnetCrawler
from .lnmtl import LNMTLCrawler
from .machinetrans import MachineNovelTrans
from .machinetransorg import MachineTransOrg
from .meionovel import MeionovelCrawler
from .mtlednovels import MtledNovelsCrawler
from .mtlnovel import MtlnovelCrawler
from .myoniyonitrans import MyOniyOniTranslation
from .novelall import NovelAllCrawler
from .novelfull import NovelFullCrawler
from .novelgo import NovelGoCrawler
from .novelonlinefull import NovelOnlineFullCrawler
from .novelplanet import NovelPlanetCrawler
from .novelraw import NovelRawCrawler
from .novelspread import NovelSpreadCrawler
from .noveluniverse import NovelUniverseCrawler
from .novelv import NovelvCrawler
from .qidiancom import QidianComCrawler
from .readln import ReadLightNovelCrawler
from .readnovelfull import ReadNovelFullCrawler
from .rebirthonline import RebirthOnlineCrawler
from .romanticlb import RomanticLBCrawler
from .royalroad import RoyalRoadCrawler
from .scribblehub import ScribbleHubCrawler
from .tapread import TapreadCrawler
from .translateindo import TranslateIndoCrawler
from .volarenovels import VolareNovelsCrawler
from .wattpad import WattpadCrawler
from .webnonline import WebnovelOnlineCrawler
from .webnovel import WebnovelCrawler
from .wordexcerpt import WordExcerptCrawler
from .worldnovelonline import WorldnovelonlineCrawler
from .wuxiaco import WuxiaCoCrawler
from .wuxiacom import WuxiaComCrawler
from .wuxiaonline import WuxiaOnlineCrawler
from .yukinovel import YukiNovelCrawler
from .zenithnovels import ZenithNovelsCrawler

crawler_list = {
    # Do not forget to append a slash(/) at the end of the url
    'http://gravitytales.com/': GravityTalesCrawler,
    'http://novelfull.com/': NovelFullCrawler,
    'http://www.machinenoveltranslation.com/': MachineNovelTrans,
    'http://www.tapread.com/': TapreadCrawler,
    'http://zenithnovels.com/': ZenithNovelsCrawler,
    'https://anythingnovel.com/': AnythingNovelCrawler,
    'https://babelnovel.com/': BabelNovelCrawler,
    'https://bestlightnovel.com/': BestLightNovel,
    'https://book.qidian.com/': QidianComCrawler,
    'https://boxnovel.com/': BoxNovelCrawler,
    'https://creativenovels.com/': CreativeNovelsCrawler,
    'https://crescentmoon.blog/': CrescentMoonCrawler,
    'https://kisslightnovels.info/': KissLightNovels,
    'https://light-novel.online/': LightNovelOnline,
    'https://litnet.com/': LitnetCrawler,
    'https://lnmtl.com/': LNMTLCrawler,
    'https://m.chinesefantasynovels.com/': ChineseFantasyNovels,
    'https://m.novelspread.com/': NovelSpreadCrawler,
    'https://m.romanticlovebooks.com/': RomanticLBCrawler,
    'https://m.wuxiaworld.co/': WuxiaCoCrawler,
    'https://meionovel.id/': MeionovelCrawler,
    'https://mtled-novels.com/': MtledNovelsCrawler,
    'https://myoniyonitranslations.com/': MyOniyOniTranslation,
    'https://novelonlinefull.com/': NovelOnlineFullCrawler,
    'https://novelplanet.com/': NovelPlanetCrawler,
    'https://novelraw.blogspot.com/': NovelRawCrawler,
    'https://readnovelfull.com/': ReadNovelFullCrawler,
    'https://webnovel.online/': WebnovelOnlineCrawler,
    'https://wordexcerpt.com/': WordExcerptCrawler,
    'https://wuxiaworld.online/': WuxiaOnlineCrawler,
    'https://www.asianhobbyist.com/': AsianHobbyistCrawler,
    'https://www.fanfiction.net/': FanFictionCrawler,
    'https://www.idqidian.us/': IdqidianCrawler,
    'https://www.jieruihao.cn/': JieruihaoCrawler,
    'https://www.machine-translation.org': MachineTransOrg,
    'https://www.mtlnovel.com/': MtlnovelCrawler,
    'https://www.novelall.com/': NovelAllCrawler,
    'https://www.novelspread.com/': NovelSpreadCrawler,
    'https://www.readlightnovel.org/': ReadLightNovelCrawler,
    'https://www.rebirth.online/': RebirthOnlineCrawler,
    'https://www.romanticlovebooks.com/': RomanticLBCrawler,
    'https://www.royalroad.com/': RoyalRoadCrawler,
    'https://www.scribblehub.com/': ScribbleHubCrawler,
    'https://www.tapread.com/': TapreadCrawler,
    'https://www.translateindo.com/': TranslateIndoCrawler,
    'https://www.volarenovels.com/': VolareNovelsCrawler,
    'https://www.wattpad.com/': WattpadCrawler,
    'https://www.webnovel.com/': WebnovelCrawler,
    'https://www.worldnovel.online/': WorldnovelonlineCrawler,
    'https://www.wuxiaworld.co/': WuxiaCoCrawler,
    'https://www.wuxiaworld.com/': WuxiaComCrawler,
    # Do not forget to append a slash(/) at the end of the url
}

rejected_sources = {
    # Do not forget to append a slash(/) at the end of the url
    'http://fullnovel.live/': '403 - Forbidden: Access is denied',
    'http://moonbunnycafe.com/': 'Does not follow uniform format',
    'https://4scanlation.com/': 'Domain expired',
    'https://comrademao.com/': 'Removed by owner',
    'https://indomtl.com/': 'Does not like to be crawled',
    'https://lnindo.org/': 'Does not like to be crawled',
    'https://novelgo.id/': 'Removed by owner',
    'https://www.noveluniverse.com/': 'Site is down',
    'https://www.novelupdates.com/': 'Does not host any novels',
    'https://www.novelv.com/': 'Site is down',
    'https://yukinovel.id/': 'Removed by owner',
    # Do not forget to append a slash(/) at the end of the url
}
