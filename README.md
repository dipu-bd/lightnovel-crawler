# Lightnovel Crawler

[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![GitHub issues](https://img.shields.io/github/issues/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/issues)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)

<!-- [![Snap Status](https://build.snapcraft.io/badge/dipu-bd/lightnovel-crawler.svg)](https://build.snapcraft.io/user/dipu-bd/lightnovel-crawler) -->

Download lightnovels from various online sources and generate output in different formats, e.g. epub, mobi, json, html, text, docx and pdf.

## Table of contents

- [Installation](#a-installation)
  - [EXE (for Windows)](#a1-exe--for-windows)
  - [Chatbots](#a2-chatbots)
    - [Telegram](#a21-telegram)
    - [Discord](#a22-discord)
  - [Python package (for Windows, Mac, and Linux)](#a3-python-package-for-windows-mac-and-linux)
  - [Run from source](#a4-run-from-source)
- [General Usage](#b-general-usage)
  - [Available options](#b1-available-options)
  - [Running the bot](#b2-running-the-bot)
- [Development](#c-development)
  - [Adding new source](#c1-adding-new-source)
  - [Adding new Bot](#c2-adding-new-bot)
  - [Supported sources](#c3-supported-sources)
  - [Supported output formats](#c4-supported-output-formats)
  - [Supported bots](#c5-supported-bots)
- [The project structure](https://github.com/dipu-bd/lightnovel-crawler/blob/master/CONTRIBUTING.md)

<img src="res/lncrawl-icon.png" width="128px" align="right"/>

## (A) Installation

### A1. EXE (for Windows)

📦 [lightnovel-crawler v2.7.13 for windows ~ 15MB](https://goo.gl/sc4EZh)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program. Actually, I am too lazy to add proper configuration files to solve this issue. Excuse me please 😇.

### A2. Chatbots

#### A2.1 Telegram

Visit this link to get started with the telegram bot:
https://t.me/epub_smelter_bot

#### A2.2 Discord

Visit this link to install discord bot to your server:
https://discordapp.com/oauth2/authorize?client_id=537526751170002946&permissions=51264&scope=bot

Send `!help` to open the bot help message.

### A3. Python package (for Windows, Mac, and Linux)

📦 A python package named `lightnovel-crawler` is available in [pypi](https://pypi.org/project/lightnovel-crawler).

> Make sure you have installed `python 3.5` or above and have `pip` enabled. Visit these links for installating python and pip in [Windows](https://stackoverflow.com/a/44437176/1583052), [Linux](https://stackoverflow.com/a/51799221/1583052) and [Mac](https://itsevans.com/install-pip-osx/). Feel free ask me if you are stuck.

To install this app or to update installed one via `pip`, just run:

```bash
$ pip install --user -U lightnovel-crawler
```

Remember, in some cases you have to use `python3 -m pip` or `pip3` or `python -m pip`. And you do not need `--user` option, if you are running from root.

Next, open your terminal and enter:

```bash
$ lightnovel-crawler

# Or, a shortcut:
$ lncrawl
```

> To view extra logs, use: `lncrawl -lll`

### A4. Run from source

- First clone the repository:

```bash
$ git clone https://github.com/dipu-bd/lightnovel-crawler
```

- Open command prompt inside of the project folder and install requirements:

```bash
$ pip install --user -r requirements.txt
```

- Run the program:

```bash
$ python3 __main__.py

# Or, in short,
$ python3 .
```

## (B) General Usage

### B1. Available options

To view list of available options:

```bash
$ lncrawl -h
================================================================================
                          📒 Lightnovel Crawler 🍀 2.7.12
            Download lightnovels into html, text, epub, mobi and json
--------------------------------------------------------------------------------
usage: 	lncrawl [options...]
	lightnovel-crawler [options...]

optional arguments:
  -h, --help            show this help message and exit
  -l                    Set log levels (1 = warn, 2 = info, 3 = debug)
  -v, --version         show program's version number and exit
  -s NOVEL_PAGE, --source NOVEL_PAGE
                        Profile page url of the novel
  -q QUERY, --query QUERY
                        Novel query followed by list of source sites.
  -o OUTPUT_PATH, --output OUTPUT_PATH
                        Path where the downloads to be stored
  --format [E [E ...]]  Ouput formats. Can be a list of the following values:
                        `epub`, `mobi`, `html`, `text`, `docx`, `pdf`
                        (default: `all`)
  -f, --force           Force replace any existing folder
  -i, --ignore          Ignore any existing folder (do not replace)
  --single              Put everything in a single book
  --multi               Build separate books by volumes
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
  --suppress            Suppress input prompts (use defaults instead)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

### B2. Running the bot

There are two chatbots available at this moment: Telegram and Discord. To run your own bot server, follow these instructions:

```bash
# Clone this repository
$ git clone https://github.com/dipu-bd/lightnovel-crawler
# Install requirements
$ pip install --user -r requirements.txt
$ pip install --user -r bot_requirements.txt
# Edit the environment variables
# You should give your API keys and log info here
# Also specify which bot server you want to run
$ cp .env.example .env
$ vim .env
# Run the server using:
$ python3 .
```

_There is a `server.sh` script to run a bot in ubuntu servers. It will basically execute the `python __main__.py` and send the task to run in background. I use it to run my discord bot in the server._

## (C) Development

You are very welcome to contribute in this project. You can:

- create new issues pointing out the bugs.
- solve existing issues.
- add your own sources.
- add new output formats.
- create new bots.

### C1. Adding new source

- Create new crawler using the [`spiders/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/spiders/_sample.py) as blueprint. You can check out existing bots for idea.
- Import your crawler to [`spiders/__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/spiders/__init__.py) file.

### C2. Adding new Bot

- Create a new bot file using [`bots/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/_sample.py) as a standard. You can check out existing bots for idea.
- Import your bot to [`bots/__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/__init__.py) file.

### C3. Supported sources

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose). Or, [make a pull request](https://github.com/dipu-bd/lightnovel-crawler/compare) by adding a new source.

The list of currently available sources and the future plans are given below:

<!-- ![search](https://img.shields.io/badge/%F0%9F%94%8D-disabled-lightgrey.svg?style=flat) -->

- [x] http://fullnovel.live ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] http://gravitytales.com
- [x] http://novelfull.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] http://www.machinenoveltranslation.com
- [x] http://zenithnovels.com
- [x] https://anythingnovel.com
- [x] https://boxnovel.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://comrademao.com
- [x] https://crescentmoon.blog
- [x] https://litnet.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://lnindo.org
- [x] https://lnmtl.com
- [x] https://m.chinesefantasynovels.com
- [x] https://m.novelspread.com
- [x] https://m.romanticlovebooks.com
- [x] https://m.wuxiaworld.co ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://m.wuxiaworld.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://meionovel.com
- [x] https://mtled-novels.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://novelonlinefree.info ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://novelplanet.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://volarenovels.com
- [x] https://webnovel.online
- [x] https://worldnovel.online ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://wuxiaworld.online ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://www.idqidian.us
- [x] https://www.novelall.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://www.novelspread.com
- [x] https://www.noveluniverse.com
- [x] https://www.novelv.com
- [x] https://www.readlightnovel.org
- [x] https://www.romanticlovebooks.com
- [x] https://www.royalroad.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://www.scribblehub.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://www.webnovel.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://www.wuxiaworld.co ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
- [x] https://www.wuxiaworld.com ![search](https://img.shields.io/badge/%F0%9F%94%8D-enabled-blue.svg?style=flat)
  <!-- Please keep the new entry sorted -->

Rejected due to difficulty or other reasons:

- [x] ~http://moonbunnycafe.com/~
- [x] ~https://www.novelupdates.com~

### C4. Supported output formats

When download is done, the following files can be generated:

- [x] JSON (default)
- [x] HTML
- [x] TEXT
- [x] EPUB
- [x] MOBI
- [x] DOCX
- [x] PDF

### C5. Supported bots

- [x] Console Bot
- [x] Telegram Bot
- [x] Discord Bot

## (D) The project structure

[Click here](https://github.com/dipu-bd/lightnovel-crawler/blob/master/CONTRIBUTING.md) to view details.
