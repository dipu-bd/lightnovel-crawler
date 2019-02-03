# Lightnovel Crawler

[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![GitHub issues](https://img.shields.io/github/issues/dipu-bd/lightnovel-crawler.svg)](https://github.com/dipu-bd/lightnovel-crawler/issues)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)

Download lightnovels from various online sources and generate output in different formats, e.g. epub, mobi, json, html, text, docx and pdf.

## Table of contents

- [General Usage](#-a--general-usage)
  - [EXE (for Windows)](#a1-exe--for-windows-)
  - [Chatbots](#a2-chatbots)
    - [Discord](#a21-discord)
  - [Python package (for Windows, Mac, and Linux)](#a3-python-package--for-windows--mac--and-linux-)
  - [Run from source](#a4-run-from-source)
  - [Available options](#a5-available-options)
  - [Running the bot](#a6-running-the-bot)
- [Development](#-b--development)
  - [Adding new source](#b1-adding-new-source)
  - [Adding new Bot](#b2-adding-new-bot)
  - [Supported sources](#b3-supported-sources)
  - [Supported output formats](#b4-supported-output-formats)
  - [Supported bots](#b5-supported-bots)
- [Getting to know the project structure](#-c--getting-to-know-the-project-structure)

<img src="res/lncrawl-icon.png" width="128px" align="right"/>

## (A) General Usage

### A1. EXE (for Windows)

📦 [lightnovel-crawler v2.7.6 for windows ~ 15MB](https://goo.gl/sc4EZh)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program. Actually, I am too lazy to add proper configuration files to solve this issue. Excuse me please 😇.

### A2. Chatbots

#### A2.1 Discord

Visit this link to install discord bot to your server:
https://discordapp.com/oauth2/authorize?client_id=537526751170002946&permissions=51264&scope=bot

Send `!help` to open the bot help message.

`<!-- Add your bot here -->`

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

### A5. Available options

To view list of available options:

```bash
$ lncrawl -h
================================================================================
                           📒 Lightnovel Crawler 🍀 2.7.6
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
  --suppress            Suppress input prompts (use defaults instead)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

### A6. Running the bot

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

*There is a `server.sh` script to run a bot in ubuntu servers. It will basically execute the `python __main__.py` and send the task to run in background. I use it to run my discord bot in the server.*

## (B) Development

You are very welcome to contribute in this project. You can:

- add your own sources
- add new output formats
- create new bots
- create new issues pointing out the bugs
- solve existing issues.

### B1. Adding new source

- Create new crawler using the [`spiders/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/spiders/_sample.py) as blueprint. You can check out existing bots for idea.
- Import your crawler to [`spiders/__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/spiders/__init__.py) file.

### B2. Adding new Bot

- Create a new bot file using [`bots/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/_sample.py) as a standard. You can check out existing bots for idea.
- Import your bot to [`bots/__init__.py`].

### B3. Supported sources

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues). Or, [make a pull request](https://github.com/dipu-bd/lightnovel-crawler/compare) by adding a new source.

The list of currently available sources and the future plans are given below:

- [x] https://lnmtl.com
- [x] https://www.webnovel.com
- [x] https://wuxiaworld.online
- [x] https://www.wuxiaworld.com
- [x] https://m.wuxiaworld.com
- [x] https://www.wuxiaworld.co
- [x] https://m.wuxiaworld.co
- [x] https://boxnovel.com
- [x] https://www.readlightnovel.org
- [x] https://novelplanet.com
- [x] https://lnindo.org
- [x] https://www.idqidian.us
- [x] https://m.romanticlovebooks.com
- [x] https://www.romanticlovebooks.com
- [x] https://webnovel.online
- [x] http://fullnovel.live
- [x] https://www.novelall.com
- [x] http://novelfull.com
- [ ] http://gravitytales.com
- [ ] http://moonbunnycafe.com/
- [ ] https://novelonlinefree.info
- [ ] https://m.novelspread.com
- [ ] https://www.noveluniverse.com/
- [ ] http://zenithnovels.com
- [ ] https://anythingnovel.com
- [ ] https://m.chinesefantasynovels.com
- [ ] http://www.machinenoveltranslation.com/

Rejected due to difficulty or other reasons:

- [x] ~https://www.novelupdates.com~
- [x] ~https://www.novelspread.com~

### B4. Supported output formats

When download is done, the following files can be generated:

- [x] JSON (default)
- [x] HTML
- [x] TEXT
- [x] EPUB
- [x] MOBI
- [x] DOCX
- [x] PDF

### B5. Supported bots

- [x] Console Bot
- [x] Telegram Bot
- [x] Discord Bot

## (C) Getting to know the project structure

- The `lncrawl` is the source folder.
- Inside `lncrawl/__init__.py` contains the execution codes.
- This file load `.env` file and calls `lncrawl/core/__init__.py`. This files loads basic settings and checks latest version.
- Next, it calls `bots/__init__.py` to start the selected bot. By default it calls the `console` bot. Otherwise, the bot specified in `.env` file will be called.
- `bots/_sample.py` is a template to create new bots.
- Inside every bot, the `core/app.py` has to be used.
- The `core/app.py` handles all user requests. It creates new crawler, do the crawling, and generate output files.
- Crawlers are inside `spiders` folder. Each crawler must extend the `utils/crawler.py` class. There is a template file: `_sample.py` inside this folder. You can use it to create new crawler.
- The `spiders/__init__.py` contains very important `crawler_list` variable, which maps the crawler class definition to url of the source.
- When user provides an input, if it is an url, then it is matched againsts this url list, and a crawler is selected. Otherwise, it will call the search functions defined in crawler instances.
- The `core` folder also has `arguments.py` file, which handles the user arguments to the console app.
- The `core/novel_info.py` process the crawled novel page, like- volume list, chapter list etc.
- The `core/downloader.py` is to download chapter list using `ThreadPoolExecutor` created by default using `5` max-workers inside `utils/crawler.py`.
- In `utils/crawler.py`, there are lots of helper methods.
  - **Do not keep any empty methods. Each methods should be implemented properly or removed from class definition.**
  - You should use `self.get_soup` to download a webpage by an URL and get an instance of `BeautifulSoup`. Check other crawlers for example.
  - `self.get_request` is to get the `response` object downloaded from given url.
  - `self.extract_contents` method takes an soup element as input, and produces a list of HTML strings containing the paragraphs of the chapter content. Before calling this method, set the `self.blacklist_patterns`, `self.block_tags` and `self.bad_tags` to customize it.
  - `novel_title`, `novel_author`, `novel_cover`, `volumes` and `chapters` should be set when getting novel info.
  - The `chapters` must contain list of all chapters of the novel. Each item must contain these keys:
    - `id`: 1 based index of the chapter
    - `title`: the title name
    - `volume`: the volume id of this chapter
    - `volume_title`: the volume title (can be ignored)
    - `url`: the link where to download the chapter
  - If you do not provide `volume_title`, it will be resolved in post-processing stage from `volume` field.
  - The `volumes` must contain a list of volumes. Each item must contain these keys:
    - `id`: 1 based index of the volume
    - `title`: the volume title (can be ignored) Create an empty volumes
  - If you do not want to use volumes, just insert this one: `{ 'id': 1, 'title': 'Volume 1' }` and set `'volume': 1` in every chapter object.
