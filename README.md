# LightNovels To EBook

Crawl website and convert it into EPUB and MOBI files

## Available Sites

- **Webnovel Crawler**: [WebNovel](https://www.webnovel.com). Also known as **Qidian**.

- **Wuxia Crawler**: [WuxiaWorld](http://www.wuxiaworld.com/).

- **LNMTL Crawler**: [LNMTL](https://lnmtl.com) - has machine translated novels.

- **ReadLN Crawler**: [ReadLightNovel](https://www.readlightnovel.org/).

## Instructions

```bash
EbookCrawler:
  python . <site-name> <novel-id> [<start-chapter>|<start-url>] [<end-chapter>|<end-url>]

OPTIONS:
site-name*   Site to crawl. Available: lnmtl, wuxia, webnovel, readln.
novel-id*    Novel id appear in url (See HINTS)
start-url    Url of the chapter to start
end-url      Url of the final chapter
start-chapter  Starting chapter
end-chapter  Ending chapter

HINTS:
- * marked params are required
- Do not provide any start or end chapter for just book binding
- Get the `novel-id` is from the link:
- `...wuxiaworld.com/desolate-era-index/de-...` = [Novel ID: `desolate-era`]
- `...lnmtl.../a-thought-through-eternity-chapter-573` = [Novel ID: `a-thought-through-eternity`]
- `...readlightnovel.../tales-of-herding-gods` = [Novel ID: `tales-of-herding-gods`]
```

### Some Examples

- Skip start index to make ebooks only: `python . wuxia desolate-era`
- Define start url: `python . wuxia desolate-era http://www.wuxiaworld.com/novel/desolate-era/de-book-1-chapter-1/`
- Define start and end url: `python . wuxia desolate-era http://www.wuxiaworld.com/novel/desolate-era/de-book-1-chapter-1/ http://www.wuxiaworld.com/novel/desolate-era/de-book-2-chapter-10`

- From webnovel:  `python . webnovel 7817013305001305 1`
- From chapter 4 to 88:  `python . webnovel 7817013305001305 4 88`

- From readln: `python . readln tales-of-herding-gods 1 10`
- From lnmtl: `python . lnmtl against-the-gods 1`

## Requirements

- Selenium: `pip install -U selenium`
- Splinter: `pip install -U splinter`
- EbookLib: `pip install -U ebooklib`
- BeautifulSoup4 - `pip install beautifulsoup4`

<!-- - KindleComicConverter: `pip install -U KindleComicConverter` -->

## Dependencies

All depencencies are stored in `/lib` folder. To update them check following links:

- Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211


##### planned

- https://www.readlightnovel.org/
