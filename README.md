# Site To Epub

Crawl website and convert it into EPUB files

## Crawlers

### 1) Wuxia Crawler

Crawler Wuxia novels and create epub/mobi files

[WuxiaWorld](http://www.wuxiaworld.com/) has many translated chinese and korean
novels. This code will convert any given book from this site into epub.

**Install requirements and run**:

- `python wuxia.py <novel-id> (<start-chapter>|<start-url>) [(<end-chapter>|<end-url>)]`

**Samples commands**:

- `python wuxia.py awe 333`
- `python wuxia.py awe 333 335`
- `python wuxia.py desolate-era http://www.wuxiaworld.com/desolate-era-index/de-book-1-chapter-1/`

### 2) LNMTL Crawler

Crawler LNMTL novels and create epub/mobi files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.

**Install requirements and run**:

- `python lnmtl.py <novel-id> <start-url> <end-url>`

**Samples commands**:

- `python wuxia.py atte https://lnmtl.com/chapter/a-thought-through-eternity-chapter-573`
- `python wuxia.py atte https://lnmtl.com/chapter/a-thought-through-eternity-chapter-573 https://lnmtl.com/chapter/a-thought-through-eternity-chapter-575`

## Requirements

- Selenium: `pip install -U selenium`
- Splinter: `pip install -U splinter`
- EbookLib: `pip install -U ebooklib`
- KindleComicConverter: `pip install -U KindleComicConverter`

## Dependencies

All depencencies are stored in `/lib` folder. To update them check following links:

- Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
