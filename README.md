# Lightnovel Crawler

[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![GitHub issues](https://img.shields.io/github/issues/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/issues)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)

<!-- [![PyPI - Format](https://img.shields.io/pypi/format/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler) -->
<!-- [![PyPI - Status](https://img.shields.io/pypi/status/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler) -->
<!-- [![GitHub contributors](https://img.shields.io/github/contributors/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler) -->
<!-- [![GitHub pull requests](https://img.shields.io/github/issues-pr/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/pulls) -->
<!-- [![GitHub closed issues](https://img.shields.io/github/issues-closed/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aclosed+) -->
<!-- [![GitHub](https://img.shields.io/github/license/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/VERSION) -->

Crawls light novels and make html, text, epub and mobi

## Tutorial

### Easy download

📦 [lightnovel-crawler v2.6.6 for windows ~ 11MB](https://goo.gl/sc4EZh)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program. Actually, I am too lazy to add proper configuration files to solve this issue. Excuse me please 😇.

### Installation

Make sure that you have `python3` and `pip` installed in your computer. Add this package using:

```bash
$ pip3 install --user -U lightnovel-crawler

# Or if it does not work, use:
$ python3 -m pip install --user -U lightnovel-crawler
```

Next, _Open the console panel in a directory you want to store your downloaded novels_ and
run the following to open an interactive console.

```bash
$ lightnovel-crawler

# Or, a shortcut:
$ lncrawl
```

To view list of available options:

```bash
$ lncrawl -h
================================================================
                   📒 Lightnovel Crawler 🍀 2.6.2
    Download lightnovels into html, text, epub, mobi and json
----------------------------------------------------------------
usage:  lncrawl [options...]
        lightnovel-crawler [options...]

optional arguments:
  -h, --help            show this help message and exit
  -l                    Set log levels (1 = warn, 2 = info, 3 = debug)
  -v, --version         show program's version number and exit
  -s NOVEL_PAGE, --source NOVEL_PAGE
                        Profile page url of the novel
  -q QUERY, --query QUERY
                        Novel query followed by list of source sites.
  -f, --force           Force replace any existing folder
  -b, --byvol           Build separate books by volumes
  --login USER PASSWD   User name/email address and password for login
  --all                 Download all chapters
  --first [COUNT]       Download first few chapters (default: 10)
  --last [COUNT]        Download last few chapters (default: 10)
  --page START STOP     The start and final chapter urls
  --range FROM TO       The start and final chapter indexes
  --volumes [N [N ...]]
                        The list of volume numbers to download
  --chapters [URL [URL ...]]
                        A list of specific chapter urls

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

> To view extra logs, use: `lncrawl -lll`

### Adding new source

- Create new crawler using the [`_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lightnovel_crawler/spiders/_sample.py) as blueprint.
- Add your crawler to [`__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lightnovel_crawler/spiders/__init__.py).

## Supported websites

The list of crawable websites are given below. _Request new site by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues)_.

- https://lnmtl.com
- https://www.webnovel.com
- https://wuxiaworld.online
- https://www.wuxiaworld.com
- https://m.wuxiaworld.com
- https://www.wuxiaworld.co
- https://m.wuxiaworld.co
- https://boxnovel.com
- https://www.readlightnovel.org
- https://novelplanet.com
- https://lnindo.org
- https://www.idqidian.us
- https://m.romanticlovebooks.com
- https://www.romanticlovebooks.com
- https://webnovel.online
- http://fullnovel.live
- https://www.novelall.com
