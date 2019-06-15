# Lightnovel Crawler

[![Build Status](https://travis-ci.com/dipu-bd/lightnovel-crawler.svg?branch=master)](https://travis-ci.com/dipu-bd/lightnovel-crawler)
[![Build status](https://ci.appveyor.com/api/projects/status/l7ci88f7ae7rxek5?svg=true)](https://ci.appveyor.com/project/dipu-bd/lightnovel-crawler)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)

<!-- [![Snap Status](https://build.snapcraft.io/badge/dipu-bd/lightnovel-crawler.svg)](https://build.snapcraft.io/user/dipu-bd/lightnovel-crawler) -->

Downloads lightnovels from various online sources and generates books in these formats: epub, mobi, json, html, text, docx and pdf.

> **Join the discord server I just opened recently: https://discord.gg/7A5Hktx**

## Table of contents

- [Installation](#a-installation)
  - [EXE (Windows)](#a1-exe-windows)
  - [PIP (Windows, Mac, and Linux)](#a2-pip-windows-mac-and-linux)
  - [Pydroid (Android)](#a3-pydroid-3-android)
  - [Chatbots](#a4-chatbots)
    - [Telegram](#a41-telegram)
    - [Discord](#a42-discord)
  - [Run from source](#a5-run-from-source)
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

### A1. EXE (Windows)

⏬ [lightnovel-crawler v2.9.12 for windows ~ 14.2MB](http://bit.ly/2I1XzeN)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program. Actually, I am too lazy to add proper configuration files to solve this issue. Excuse me please 😇.

_PDF and DOCX generation is disabled for EXE build. It only works with `pip`_

### A2. PIP (Windows, Mac, and Linux)

📦 A python package named `lightnovel-crawler` is available in [pypi](https://pypi.org/project/lightnovel-crawler).

> Make sure you have installed `python 3.5` or above and have `pip` enabled. Visit these links for installating python and pip in [Windows](https://stackoverflow.com/a/44437176/1583052), [Linux](https://stackoverflow.com/a/51799221/1583052) and [Mac](https://itsevans.com/install-pip-osx/). Feel free ask me if you are stuck.

To install this app or to update installed one via `pip`, just run:

```bash
$ pip install --user -U lightnovel-crawler
```

Remember, in some cases you have to use `python3 -m pip` or `pip3` or `python -m pip`. And you do not need `--user` option, if you are running from root.

> **To Windows users:** Download and install the GTK3-Runtime from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

Next, open your terminal and enter:

```bash
$ lightnovel-crawler

# Or, a shortcut:
$ lncrawl
```

> To view extra logs, use: `lncrawl -lll`

### A3. Pydroid 3 (Android)

📱 You can run this app in your android phones too. Here are the steps to do:

- Install [Pydriod 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3&hl=en) from playstore.
- Open the app and navigate to **Pip** from the drawer menu.
- Type `lightnovel-crawler` in place of `Library name` and press the `Install` button.
- To reinstall or remove the installed package:
  - Go to _Libraries_ tab inside **Pip** page (left of _Install_ tab).
  - Find `lightnovel-crawler` and press the `Uninstall` button.
  - Then go over to _Install_ tab again to install the latest version.
- To use the app, select **Terminal** from the drawer menu. A console will appear.
- Type `lncrawl` to start.
- You navigate up using <kbd>Volume UP</kbd> + <kbd>W</kbd> and down using <kbd>Volume UP</kbd> + <kbd>S</kbd>.

> Here is a video that might help: https://youtu.be/I20IO4dGTJ8

### A4. Chatbots

#### A4.1 Telegram

Visit this link to get started with the telegram bot:
https://t.me/epub_smelter_bot

#### A4.2 Discord

Visit this link to install discord bot to your server:
https://discordapp.com/oauth2/authorize?client_id=537526751170002946&permissions=51264&scope=bot

Send `!help` to open the bot help message.

### A5. Run from source

- First clone the repository:

```bash
$ git clone https://github.com/dipu-bd/lightnovel-crawler
```

- Open command prompt inside of the project folder and install requirements:

```bash
$ pip3 install --user -r requirements.txt
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
                           📒 Lightnovel Crawler 🍀2.9.12
            Download lightnovels into html, text, epub, mobi and json
--------------------------------------------------------------------------------
usage: lncrawl [options...]
       lightnovel-crawler [options...]

positional arguments:
  EXTRA                 To pass a query string to use as extra arguments

optional arguments:
  -h, --help            show this help message and exit
  -l                    Set log levels (1 = warn, 2 = info, 3 = debug)
  -v, --version         show program's version number and exit
  -s URL, --source URL  Profile page url of the novel
  -q STR, --query STR   Novel query followed by list of source sites.
  --sources             Display the source selection menu while searching
  -o PATH, --output PATH
                        Path where the downloads to be stored
  --format E [E ...]    Define which formats to output. Default: all
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
  --bot {console,telegram,discord,test}
                        Select a bot. Default: console

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

### B2. Running the bot

There are two chatbots available at this moment: Telegram and Discord. To run your own bot server, follow these instructions:

```bash
# Clone this repository
$ git clone https://github.com/dipu-bd/lightnovel-crawler
# Install requirements
$ pip3 install --user -r requirements.txt
$ pip3 install --user -r bot_requirements.txt
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

| Available Sources                      | Search Enable |
| -------------------------------------- | :-----------: |
| http://gravitytales.com                |               |
| http://novelfull.com                   |       ✔       |
| http://www.machinenoveltranslation.com |               |
| http://zenithnovels.com                |               |
| https://anythingnovel.com              |               |
| https://babelnovel.com/                |       ✔       |
| https://bestlightnovel.com             |       ✔       |
| https://boxnovel.com                   |       ✔       |
| https://comrademao.com                 |               |
| https://creativenovels.com             |               |
| https://crescentmoon.blog              |               |
| https://litnet.com                     |       ✔       |
| https://lnmtl.com                      |               |
| https://m.chinesefantasynovels.com     |               |
| https://m.novelspread.com              |               |
| https://m.romanticlovebooks.com        |               |
| https://m.wuxiaworld.co                |       ✔       |
| https://meionovel.com                  |               |
| https://mtled-novels.com               |       ✔       |
| https://myoniyonitranslations.com      |               |
| https://novelplanet.com                |       ✔       |
| https://novelraw.blogspot.com          |               |
| https://volarenovels.com               |               |
| https://webnovel.online                |               |
| https://wuxiaworld.online              |       ✔       |
| https://www.idqidian.us                |               |
| https://www.novelall.com               |       ✔       |
| https://www.novelspread.com            |               |
| https://www.readlightnovel.org         |               |
| https://www.readnovelfull.com          |       ✔       |
| https://www.romanticlovebooks.com      |               |
| https://www.royalroad.com              |       ✔       |
| https://www.scribblehub.com            |       ✔       |
| https://www.tapread.com                |               |
| https://www.webnovel.com               |       ✔       |
| https://www.worldnovel.online          |       ✔       |
| https://www.wuxiaworld.co              |       ✔       |
| https://www.wuxiaworld.com             |       ✔       |
| https://yukinovel.me                   |               |

Rejected:

| Rejected Sources              | Reason                              |
| ----------------------------- | ----------------------------------- |
| https://4scanlation.xyz       | `ERR_SSL_PROTOCOL_ERROR`            |
| http://fullnovel.live         | `403 - Forbidden: Access is denied` |
| http://moonbunnycafe.com      | `Does not follow uniform format`    |
| https://indomtl.com           | `Does not like to be crawled`       |
| https://lnindo.org            | `Does not like to be crawled`       |
| https://www.noveluniverse.com | `Site is down`                      |
| https://www.novelupdates.com  | `Does not host any novels`          |
| https://www.novelv.com        | `Site is down`                      |

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
