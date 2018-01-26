# Site To Epub

Crawl website and convert it into EPUB files

### Crawlers

### LNMTL Crawler

Crawler LNMTL novels and create epub/mobi files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.

- Run `python lnmtl.py <novel-id> <start-url> <end-url>`

## Requirements

- Selenium: `pip install -U selenium`
- Splinter: `pip install -U splinter`
- Pypub: `pip install -U pypub`
- KindleComicConverter: `pip install KindleComicConverter`

## Dependencies

All depencencies are stored in `/lib` folder. To update them check following links:

- Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
