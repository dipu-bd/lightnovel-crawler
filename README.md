# Site To Epub

Crawl website and convert it into EPUB files

## LNMTL Crawler

Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.

### Requirements

- Selenium: conda install -c conda-forge selenium
- Splinter: conda install -c metaperl splinter
- Pypub: pip install pypub
- Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- Make `chromedriver` accessible via terminal
- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
- Make `kindlegen` accessible via terminal

### Execute program

- Change settings in `lnmtl_settings.py`
- Run `python lnmtl.py` to start crawling
