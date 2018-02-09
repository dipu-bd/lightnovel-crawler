# Site To Epub

Crawl website and convert it into EPUB files

## Available Sites

- **Webnovel Crawler**: [WebNovel](https://www.webnovel.com) is a website of english translated
chinese/korean/japanese light novels. Also known as **Qidian**.

- **Wuxia Crawler**: [WuxiaWorld](http://www.wuxiaworld.com/) has many translated chinese and korean novels. This code will convert any given book from this site into epub.

- **LNMTL Crawler**: [LNMTL](https://lnmtl.com) is a website containing machine translated novels. This code will convert any given book from this site into epub.

## Instructions

```bash
EbookCrawler:
  python . <site-name> <novel-id> [<start-chapter>|<start-url>] [<end-chapter>|<end-url>]

OPTIONS:
site-name*   Site to crawl. Available: lnmtl, wuxia, webnovel.
novel-id*    Novel id appear in url (See HINTS)
start-url    Url of the chapter to start
end-url      Url of the final chapter
end-chapter  Starting chapter
end-chapter  Ending chapter

HINTS:
- * marked params are required
- Do not provide any start or end chapter for just book binding
- Novel id of: `...wuxiaworld.com/desolate-era-index/de-...` is `desolate-era`
- Novel id of: `...lnmtl.../a-thought-through-eternity-chapter-573` is `a-thought-through-eternity`
```

### Some Examples

- Skip start index to make eBook only: `python . wuxia awe`
- All chapters from 333: `python . wuxia awe 333`
- Chapter 333 to 335: `python . wuxia awe 333 335`
- Define start url: `python . wuxia desolate-era http://www.wuxiaworld.com/desolate-era-index/de-book-1-chapter-1/`
- Define start and end url: `python . wuxia desolate-era http://www.wuxiaworld.com/desolate-era-index/de-book-1-chapter-1/ http://www.wuxiaworld.com/desolate-era-index/de-book-2-chapter-10`
- From webnovel:  `python . webnovel 7817013305001305 1`

## Requirements

- Selenium: `pip install -U selenium`
- Splinter: `pip install -U splinter`
- EbookLib: `pip install -U ebooklib`
- KindleComicConverter: `pip install -U KindleComicConverter`

## Dependencies

All depencencies are stored in `/lib` folder. To update them check following links:

- Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
