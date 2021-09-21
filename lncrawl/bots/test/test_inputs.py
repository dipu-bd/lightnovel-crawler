# -*- coding: utf-8 -*-
from base64 import decodestring as b64decode

allowed_failures = [
    'https://ranobelib.me/',
    'https://www.aixdzs.com/',
    'https://webnovelindonesia.com/',
    'http://tiknovel.com/',
    'http://www.tiknovel.com/',
    'https://www.tiknovel.com/',
    'https://m.webnovel.com/',
    'https://m.readlightnovel.cc',
    'https://dmtranslationscn.com/',
    'https://m.wuxiaworld.co/',
    'http://www.fujitranslation.com/',
    'https://m.mywuxiaworld.com/',
    'https://m.readlightnovel.cc/',
    b64decode("aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS8=".encode()).decode()
]

test_user_inputs = {
    b64decode("aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS8=".encode()).decode(): [
        b64decode(
            "aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS9ub3ZlbC90c3VydWdpLW5vLWpvb3UtdG8tcmFrdWluLW5vLWtvLw==".encode()).decode()
    ],
    'https://fastnovel.net/': [
        'https://fastnovel.net/nanomancer-reborn-ive-become-a-snow-girl-156/'
    ],
    'https://www.readlightnovel.cc/': [
        'https://www.readlightnovel.cc/Heidi-and-the-Lord/'
    ],
    'https://www.mywuxiaworld.com/': [
        'https://www.mywuxiaworld.com/book/Rebirth_of_the_Thief_Who_Roamed_the_World/'
    ],
    'http://www.indonovels.net/': [
        'http://www.indonovels.net/p/blog-page_1.html'
    ],
    'https://fujitranslation.com/': [
        'https://fujitranslation.com/mkw/'
    ],
    'https://indowebnovel.id/': [
        'https://indowebnovel.id/novel/rebirth-of-the-urban-immortal-cultivator/'
    ],
    'https://jpmtl.com/': [
        'https://jpmtl.com/books/178'
    ],
    'https://wbnovel.com/': [
        'https://wbnovel.com/novel/genius-detective/'
    ],
    'https://woopread.com/': [
        'https://woopread.com/series/the-villainess-lives-twice/'
    ],
    'https://www.novelhall.com/': [
        'https://www.novelhall.com/best-to-have-met-you-14935/'
    ],
    'https://mangatoon.mobi/': [
        'https://mangatoon.mobi/en/detail/40627'
    ],
    'https://es.mtlnovel.com/': [
        'https://es.mtlnovel.com/being-a-hamster-in-the-apocalypse-is-a-breeze/',
    ],
    'https://fr.mtlnovel.com/': [
        'https://fr.mtlnovel.com/being-a-hamster-in-the-apocalypse-is-a-breeze/',
    ],
    'https://novelsrock.com/': [
        'https://novelsrock.com/novel/the-man-from-hell-2/',
        'kuro'
    ],
    'http://gravitytales.com/': [
        'http://gravitytales.com/posts/novel/a-dragons-curiosity'
    ],
    'https://novelfull.com/': [
        'https://novelfull.com/dungeon-defense.html',
    ],
    'http://novelfull.com/': [
        'Sinister Ex Girlfriend',
    ],
    'http://www.machinenoveltranslation.com/': [
        'http://www.machinenoveltranslation.com/a-thought-through-eternity',
    ],
    'http://zenithnovels.com/': [
        'http://zenithnovels.com/infinity-armament/',
    ],
    'https://anythingnovel.com/': [
        'https://anythingnovel.com/novel/king-of-gods/',
    ],
    'https://boxnovel.com/': [
        'https://boxnovel.com/novel/the-rest-of-my-life-is-for-you/',
        'cultivation chat',
    ],
    'https://crescentmoon.blog/': [
        'https://crescentmoon.blog/dark-blue-and-moonlight/',
    ],
    'https://litnet.com/': [
        'https://litnet.com/en/book/candy-lips-1-b106232',
        'candy lips',
    ],
    'https://lnmtl.com/': [
        'https://lnmtl.com/novel/i-really-just-want-to-die',
    ],
    'https://m.chinesefantasynovels.com/': [
        'https://m.chinesefantasynovels.com/3838/',
    ],
    'https://m.novelspread.com/': [
        'https://m.novelspread.com/novel/the-legend-of-the-concubine-s-daughter-minglan',
    ],
    'https://m.romanticlovebooks.com/': [
        'https://m.romanticlovebooks.com/xuanhuan/207.html',
    ],
    'https://9kqw.com/': [
        'https://9kqw.com/book/index?id=717',
    ],
    'https://www.wuxiaworld.co/': [
        'https://www.wuxiaworld.co/Versatile-Mage/',
    ],
    'https://meionovel.id/': [
        'https://meionovel.id/novel/the-legendary-mechanic/',
    ],
    'https://mtled-novels.com/': [
        'https://mtled-novels.com/novels/great-ruler/',
        'great ruler'
    ],
    'https://bestlightnovel.com/': [
        'https://bestlightnovel.com/novel_888103800',
        'martial'
    ],
    'https://novelplanet.com/': [
        'https://novelplanet.com/Novel/Returning-from-the-Immortal-World',
        'immortal'
    ],
    'https://www.volarenovels.com/': [
        'https://www.volarenovels.com/novel/adorable-creature-attacks',
    ],
    'https://webnovel.online/': [
        'https://webnovel.online/full-marks-hidden-marriage-pick-up-a-son-get-a-free-husband',
    ],
    'https://www.idqidian.us/': [
        'https://www.idqidian.us/novel/peerless-martial-god/'
    ],
    'https://www.novelall.com/': [
        'https://www.novelall.com/novel/Virtual-World-Close-Combat-Mage.html',
        'combat'
    ],
    'https://www.novelspread.com/': [
        'https://www.novelspread.com/novel/the-legend-of-the-concubine-s-daughter-minglan'
    ],
    'https://www.readlightnovel.org/': [
        'https://www.readlightnovel.org/top-furious-doctor-soldier'
    ],
    'https://www.romanticlovebooks.com/': [
        'https://www.romanticlovebooks.com/xianxia/251.html'
    ],
    'https://www.royalroad.com/': [
        'https://www.royalroad.com/fiction/21220/mother-of-learning',
        'mother'
    ],
    'https://www.scribblehub.com/': [
        'https://www.scribblehub.com/series/73550/modern-life-of-the-exalted-immortal/',
        'cultivation'
    ],
    'https://www.webnovel.com/': [
        'https://www.webnovel.com/book/8212987205006305/Trial-Marriage-Husband%3A-Need-to-Work-Hard',
        'martial',
    ],
    'https://www.worldnovel.online/': [
        'https://www.worldnovel.online/novel/solo-leveling/',
    ],
    'https://rewayat.club/': [
        'https://rewayat.club/novel/almighty-sword-domain/'
    ],
    'https://www.wuxiaworld.com/': [
        'https://www.wuxiaworld.com/novel/martial-god-asura',
        'martial',
    ],
    'https://creativenovels.com/': [
        'https://creativenovels.com/novel/eternal-reverence/',
    ],
    'https://www.tapread.com/': [
        'https://www.tapread.com/book/detail/80',
    ],
    'http://www.tapread.com/': [
        'http://www.tapread.com/book/detail/80',
    ],
    'https://readnovelfull.com/': [
        'https://readnovelfull.com/lord-of-all-realms.html',
        'cultivation'
    ],
    'https://myoniyonitranslations.com/': [
        'https://myoniyonitranslations.com/top-management/',
        'https://myoniyonitranslations.com/category/god-of-tennis',
    ],
    'https://babelnovel.com/': [
        'https://babelnovel.com/books/ceo-let-me-go',
        'dazzle Good'
    ],
    'https://wuxiaworld.online/': [
        'https://wuxiaworld.online/trial-marriage-husband-need-to-work-hard',
        'cultivation',
    ],
    'https://www.novelv.com/': [
        'https://www.novelv.com/0/349/'
    ],
    'http://fullnovel.live/': [
        'http://fullnovel.live/novel-a-will-eternal',
        'will eternal',
    ],
    'https://www.noveluniverse.com/': [
        'https://www.noveluniverse.com/index/novel/info/id/15.html'
    ],
    'https://novelraw.blogspot.com/': [
        'https://novelraw.blogspot.com/2019/02/another-worlds-versatile-crafting.html'
    ],
    'https://light-novel.online/': [
        'https://light-novel.online/great-tyrannical-deity',
        'tyrannical'
    ],
    'https://www.rebirth.online/': [
        'https://www.rebirth.online/novel/upside-down'
    ],
    'https://www.jieruihao.cn/': [
        'https://www.jieruihao.cn/novel/against-the-gods/',
    ],
    'https://www.wattpad.com/': [
        'https://www.wattpad.com/story/87505567-loving-mr-jerkface-%E2%9C%94%EF%B8%8F'
    ],
    'https://novelgo.id/': [
        'https://novelgo.id/novel/the-mightiest-leveling-system/'
    ],
    'https://yukinovel.me/': [
        'https://yukinovel.me/novel/the-second-coming-of-avarice/',
    ],
    'https://www.asianhobbyist.com/': [
        'https://www.asianhobbyist.com/series/that-time-i-got-reincarnated-as-a-slime/'
    ],
    'https://kisslightnovels.info/': [
        'https://kisslightnovels.info/novel/solo-leveling/'
    ],
    'https://novelonlinefull.com/': [
        'https://novelonlinefull.com/novel/abo1520855001564322110'
    ],
    'https://www.machine-translation.org/': [
        'https://www.machine-translation.org/novel/bace21c9b10d34e9/world-of-cultivation.html'
    ],
    'https://www.fanfiction.net/': [
        'https://www.fanfiction.net/s/7268451/1/Facebook-For-wizards'
    ],
    'https://www.mtlnovel.com/': [
        'https://www.mtlnovel.com/trapped-in-a-typical-idol-drama/'
    ],
    'https://wordexcerpt.com/': [
        'https://wordexcerpt.com/series/transmigration-raising-the-child-of-the-male-lead-boss/'
    ],
    'https://www.translateindo.com/': [
        'https://www.translateindo.com/demon-wang-golden-status-favoured-fei/'
    ],
    'https://ranobelib.me/': [
        'https://ranobelib.me/sozvezdie-klinka'
    ],
    'https://novelringan.com/': [
        'https://novelringan.com/series/the-most-loving-marriage-in-history-master-mus-pampered-wife/'
    ],
    'https://wuxiaworld.site/': [
        'https://wuxiaworld.site/novel/only-i-level-up/'
    ],
    'https://id.mtlnovel.com/': [
        'https://id.mtlnovel.com/the-strongest-plane-becomes-god/'
    ],
    'https://www.shinsori.com/': [
        'https://www.shinsori.com/akuyaku-reijou-ni-nanka-narimasen/'
    ],
    'https://www.flying-lines.com/': [
        'https://www.flying-lines.com/novel/one-useless-rebirth'
    ],
    'https://book.qidian.com/': [
        'https://book.qidian.com/info/1016597088'
    ],
    'https://kiss-novel.com/': [
        'https://kiss-novel.com/the-first-order'
    ],
    'https://www.machine-translation.org/': [
        'https://www.machine-translation.org/novel/a5eee127d75da0d2/long-live-summons.html'
    ],
    'https://www.aixdzs.com/': [
        'https://www.aixdzs.com/d/66/66746/'
    ],
    'https://webnovelonline.com/': [
        'https://webnovelonline.com/novel/the_anarchic_consort'
    ],
    'https://4scanlation.com/': [
        'https://4scanlation.com/tensei-shitara-slime-datta-ken-wn/'
    ],
    'https://listnovel.com/': [
        'https://listnovel.com/novel/my-sassy-crown-princess/'
    ],
    'https://tomotranslations.com/': [
        'https://tomotranslations.com/this-hero-is-invincible-but-too-cautious/'
    ],
    'https://www.wuxialeague.com/': [
        'https://www.wuxialeague.com/novel/245/'
    ],
    'http://liberspark.com/': [
        'http://liberspark.com/novel/black-irons-glory'
    ],
    'https://webnovelindonesia.com/': [
        'https://webnovelindonesia.com/nv/the-beginning-after-the-end/'
    ],
    'https://tiknovel.com/': [
        'https://tiknovel.com/book/index?id=717'
    ],
    'http://boxnovel.org/': [
        'http://boxnovel.org/novel/the-fierce-illegitimate-miss'
    ],
    'https://instadoses.com/': [
        'https://instadoses.com/manga/martial-arts-reigns/'
    ],
    'https://foxaholic.com/': [
        'https://foxaholic.com/novel/the-white-eyed-wolves-i-personally-raised-are-all-coveting-my-legacy/'
    ],
    'https://readlightnovels.net/': [
        'https://readlightnovels.net/death-march-kara-hajimaru-isekai-kyusoukyoku.html'
    ],
    'https://isotls.com/': [
        'https://isotls.com/poisonous-peasant-concubine/'
    ],
    'https://lazybirdtranslations.wordpress.com/': [
        'https://lazybirdtranslations.wordpress.com/the-prestigious-familys-young-lady-and-the-farmer/'
    ],
    'https://www.novelmultiverse.com/': [
        'https://www.novelmultiverse.com/novel/the-fierce-illegitimate-miss/'
    ],
    'https://readnovelz.net/': [
        'https://readnovelz.net/read/rebirth-how-a-loser-became-a-prince-charming/'
    ],
    'https://rpgnovels.com/': [
        'https://rpgnovels.com/the-demon-lords-urban-development-the-strongest-dungeon-is-a-modern-day-town/'
    ],
    'https://dobelyuwai.wordpress.com/': [
        'https://dobelyuwai.wordpress.com/to-be-a-power-in-the-shadows-ln-volume-4/'
    ],
    'https://cclawtranslations.home.blog/': [
        'https://cclawtranslations.home.blog/asahina-wakaba-to-marumaru-na-kareshi-toc/'
    ],
    'https://wujizun.com/': [
        'https://wujizun.com/mysd/'
    ],
    'https://novelmic.com/': [
        'https://novelmic.com/manga/tales-of-demons-and-gods-comics/'
    ],
    'https://www.1ksy.com/': [
        'https://www.1ksy.com/120_120546/'
    ],
    'http://readonlinenovels.com/': [
        'http://readonlinenovels.com/nv/244c8160d7f91754/hail-the-king-h'
    ],
    'https://arnovel.me/': [
        'https://arnovel.me/novel/%d8%b2%d9%88%d8%ac%d8%aa%d9%87-%d8%a7%d9%84%d8%b9%d8%a8%d9%82%d8%b1%d9%8a%d8%a9-%d9%86%d8%ac%d9%85%d8%a9/'
    ],
    'https://lightnovelshub.com/': [
        'https://lightnovelshub.com/novel/strongest-abandoned-son/'
    ],
    'https://smnovels.com/': [
        'https://smnovels.com/category/novel/a-dish-best-served-cold/'
    ],
    'https://www.wnmtl.org/': [
        'https://www.wnmtl.org/novel/the-amber-sword/'
    ],
    'https://tw.m.ixdzs.com/': [
        'https://tw.m.ixdzs.com/novel/%E6%88%91%E7%95%B6%E9%99%B0%E9%99%BD%E5%85%88%E7%94%9F%E7%9A%84%E9%82%A3%E5%B9%BE%E5%B9%B4'
    ],
    'https://noveltrench.com/': [
        'https://noveltrench.com/manga/refining-the-mountains-and-rivers/'
    ],
    'https://tipnovel.com/': [
        'https://tipnovel.com/novel/profound-dragon-warlord/'
    ],
    'https://f-w-o.com/': [
        'https://f-w-o.com/novel/lord-of-flames/'
    ],
    'https://lightnovelheaven.com/': [
        'https://lightnovelheaven.com/series/martial-god-asura/'
    ],
    'https://lunarletters.com/': [
        'https://lunarletters.com/series/the-royal-deal/'
    ],
    'https://noveltranslate.com/': [
        'https://noveltranslate.com/novel/earth-destruction-plan/'
    ],
    'https://omgnovels.com/': [
        'https://omgnovels.com/novel/master-hunter-k/'
    ],
    'https://webnovelonline.net/': [
        'https://webnovelonline.net/read/peerless-martial-god/'
    ],
    'https://sleepytranslations.com/': [
        'https://sleepytranslations.com/series/semantic-error/'
    ],
    'https://supernovel.net/': [
        'https://supernovel.net/novel/moonlight-ball/'
    ],
    'https://vipnovel.com/': [
        'https://vipnovel.com/vipnovel/supreme-crazy-wife/'
    ],
    'https://zinnovel.com/': [
        'https://zinnovel.com/manga/under-the-oak-tree/'
    ]
}
