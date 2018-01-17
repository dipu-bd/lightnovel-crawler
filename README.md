# Site To Epub

Crawl website and convert it into EPUB files

## LNMTL Crawler

Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.

##### Execute program

- Change settings in `lnmtl_settings.py`
- Run `python lnmtl.py` to start crawling

##### Requirements

- Selenium: `pip install -U selenium`
- Splinter: `pip install -U splinter`
- Pypub: `pip install -U pypub`

#### Dependencies

All depencencies are stored in `/lib` folder. To update them check following links:

- Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- Make `chromedriver` accessible via terminal
- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
- Make `kindlegen` accessible via terminal
