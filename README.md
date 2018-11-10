# LightNovels To EBook

[![Python version](https://img.shields.io/pypi/pyversions/ebook-crawler.svg)](https://pypi.org/project/ebook-crawler)
[![PyPI version](https://img.shields.io/pypi/v/ebook-crawler.svg)](https://pypi.org/project/ebook-crawler)
[![PyPI - Format](https://img.shields.io/pypi/format/ebook-crawler.svg)](https://pypi.org/project/ebook-crawler)
[![PyPI - Status](https://img.shields.io/pypi/status/ebook-crawler.svg)](https://pypi.org/project/ebook-crawler)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)
<br>
[![GitHub contributors](https://img.shields.io/github/contributors/dipu-bd/site-to-epub.svg)](https://github.com/dipu-bd/site-to-epub)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/dipu-bd/site-to-epub.svg)](https://github.com/dipu-bd/site-to-epub/pulls)
[![GitHub issues](https://img.shields.io/github/issues/dipu-bd/site-to-epub.svg)](https://github.com/dipu-bd/site-to-epub/issues)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/dipu-bd/site-to-epub.svg)](https://github.com/dipu-bd/site-to-epub/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aclosed+)
[![GitHub](https://img.shields.io/github/license/dipu-bd/site-to-epub.svg)](https://github.com/dipu-bd/site-to-epub/blob/master/VERSION)

Crawls lightnovels from popular websites and converts to ebook format (only EPUB and MOBI are supported for now).

## Tutorial

### Installation

You must have `python3` and `pip` installed in your computer. Install the package using:

```bash
$ pip install ebook-crawler

# Or,
$ python3 -m pip install --user ebook-crawler
```

*Open the console panel in a directory you want to download novels* and run:

```bash
$ ebook_crawler
```

For extra logs, there is verbose mode:
```bash
$ ebook_crawler --verbose
```

### Dependencies

#### MOBI Output

- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211

#### NodeJS for cloudflare

Some websites like `novelplanet` needs `nodejs`. Install it from:

- Downloads: https://nodejs.org/en/download/ 
- Linux: `curl -sL https://deb.nodesource.com/setup_8.x -o nodesource_setup.sh`

### Available websites

The avaiable list of site handles are given below. *To request new site [create a new issues](https://github.com/dipu-bd/site-to-epub/issues) requesting it*.

- https://lnmtl.com
- https://www.webnovel.com
- https://www.wuxiaworld.com
- https://www.wuxiaworld.co
- https://boxnovel.com
- https://www.readlightnovel.org
- https://novelplanet.com
- https://lnindo.org
- https://www.idqidian.us

#### Be a good Netizen

- Do not download too frequently from LNTML. They block your IP if too many consecutive request is observed.

- Do not use too many instances of this program too frequently. Otherwise it might cause traffic jam to your favorite website. We do not want others to suffer for our sake, right?

- This program has the capability to perform DDOS attacks that can cause a website to go down. Be a good netizen, and never do such a thing!

## Adding new source

- Use the [`_sample.py`](https://github.com/dipu-bd/site-to-epub/blob/master/ebook_crawler/_sample.py) as blueprint.
- Add your crawler to [`__init__.py`](https://github.com/dipu-bd/site-to-epub/blob/master/ebook_crawler/__init__.py).

That's all!
