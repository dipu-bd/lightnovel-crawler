# Lightnovel Crawler

[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![GitHub issues](https://img.shields.io/github/issues/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/issues)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)
<!-- [![PyPI - Format](https://img.shields.io/pypi/format/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler) -->
<!-- [![PyPI - Status](https://img.shields.io/pypi/status/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler) -->
<!-- [![GitHub contributors](https://img.shields.io/github/contributors/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler) -->
<!-- [![GitHub pull requests](https://img.shields.io/github/issues-pr/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/pulls) -->
<!-- [![GitHub closed issues](https://img.shields.io/github/issues-closed/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aclosed+) -->
<!-- [![GitHub](https://img.shields.io/github/license/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/VERSION) -->

Crawls light novels and make text, epub and mobi

## Tutorial

### Installation

Make sure that you have `python3` and `pip` installed in your computer. Add this package using:

```bash
$ pip3 install -U lightnovel-crawler

# Or if it does not work, use:
$ python3 -m pip install --user -U lightnovel-crawler
```

Next, *Open the console panel in a directory you want to store your downloaded novels* and
run the following to open an interactive console.

```bash
$ lightnovel-crawler

# Or, a shortcut:
$ lncrawl
```

> There is a verbose mode for extended logging: `lncrawl -v`

### Available websites

The list of crawable websites are given below. *Request new site by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues)*.

- https://lnmtl.com
- https://www.webnovel.com
- https://wuxiaworld.online
- https://www.wuxiaworld.com
- https://www.wuxiaworld.co
- https://boxnovel.com
- https://www.readlightnovel.org
- https://novelplanet.com
- https://lnindo.org
- https://www.idqidian.us

## Adding new source

- Use the [`_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lightnovel_crawler/_sample.py) as blueprint.
- Add your crawler to [`__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lightnovel_crawler/__init__.py).

That's all!
