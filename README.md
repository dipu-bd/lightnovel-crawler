# Lightnovel Crawler

[![Build Status](https://travis-ci.com/dipu-bd/lightnovel-crawler.svg?branch=master)](https://travis-ci.com/dipu-bd/lightnovel-crawler)
[![Build status](https://ci.appveyor.com/api/projects/status/l7ci88f7ae7rxek5?svg=true)](https://ci.appveyor.com/project/dipu-bd/lightnovel-crawler)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![SayThanks.io](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/dipu-bd)

<!-- [![Heroku](https://heroku-badge.herokuapp.com/?app=lncrawl)] -->
<!-- [![Snap Status](https://build.snapcraft.io/badge/dipu-bd/lightnovel-crawler.svg)](https://build.snapcraft.io/user/dipu-bd/lightnovel-crawler) -->

Downloads lightnovels from various online sources and generates ebooks in many formats.

> **Discord: https://discord.gg/7A5Hktx**

> **Telegram: https://t.me/epub_smelter_bot**

## Table of contents

- [Installation](#a-installation)
  - [⏬ Standalone Bundle (Windows, Linux)](#a1-standalone-bundle-windows-linux)
  - [📦 PIP (Windows, Mac, and Linux)](#a2-pip-windows-mac-and-linux)
  - [📱 Termux (Android)](#a3-termux-android)
  - [📱 Pydroid (Android)](#a4-pydroid-3-android)
  - [Chatbots](#a5-chatbots)
    - [Telegram](#a51-telegram)
    - [Discord](#a52-discord)
  - [Run from source](#a6-run-from-source)
  - [Heroku Deployment](#a7-heroku-deployment)
- [General Usage](#b-general-usage)
  - [Available options](#b1-available-options)
  - [Running the bot](#b2-running-the-bot)
- [Development](#c-development)
  - [Adding new source](#c1-adding-new-source)
  - [Adding new Bot](#c2-adding-new-bot)
  - [Supported sources](#c3-supported-sources)
  - [Rejected sources](#c4-rejected-sources)
  - [Supported output formats](#c5-supported-output-formats)
  - [Supported bots](#c6-supported-bots)
- [The project structure](https://github.com/dipu-bd/lightnovel-crawler/blob/master/CONTRIBUTING.md)

<img src="res/lncrawl-icon.png" width="128px" align="right"/>

## (A) Installation

**This application uses _Calibre_ to convert ebooks.** <br>
**Install it from https://calibre-ebook.com/download** <br>
Without it, you will only get output in epub, text, and web formats.

Also, you have to install **node.js** to access cloudflare enabled sites (e.g. https://novelplanet.com/). Download and install node.js from here: https://nodejs.org/en/download/

### A1. Standalone Bundle (Windows, Linux)

⏬ **Windows**: [lightnovel-crawler v2.16.2 ~ 21MB](http://bit.ly/2I1XzeN)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program. Actually, I am too lazy to add proper configuration files to solve this issue. Excuse me please 😇.

⏬ **Linux**: [lightnovel-crawler v2.16.0 ~ 27MB](http://bit.ly/2LaB9HB)

> Copy it to `/usr/bin` or `~/.local/bin` to make it accessible in terminal. Or, you can [create a launcher](https://askubuntu.com/a/66918/457551) to easily access the app.

### A2. PIP (Windows, Mac, and Linux)

📦 A python package named `lightnovel-crawler` is available at [pypi](https://pypi.org/project/lightnovel-crawler).

> Make sure you have installed **Python** v3.5 or higher and have **pip** enabled. Visit these links to install python with pip in [Windows](https://stackoverflow.com/a/44437176/1583052), [Linux](https://stackoverflow.com/a/51799221/1583052) and [MacOS](https://itsevans.com/install-pip-osx/). Feel free to ask on the Discord server if you are stuck.

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

### A3. Termux (Android)

📱 Using Termux, you can run this app in your android phones too. Follow this instructions:

- Install [Termux](https://play.google.com/store/apps/details?id=com.termux) from playstore.
- Open the app and run these commands one by one:
  - `apt update && apt upgrade`
  - `termux-setup-storage`
  - `pkg install ndk-sysroot make python zlib clang`
  - `pkg install libxml2 libxslt libiconv libcrypt libffi zlib libjpeg-turbo`
  - `pkg install nodejs-lts`
  - `pip install -U lightnovel-crawler` to install the latest version of this app.
- Now exit the console and relaunch it.
- Type `cd ~/storage/downloads` to store novels there.
- Type `lncrawl` to start.
- You navigate up using <kbd>Volume UP</kbd> + <kbd>W</kbd> and down using <kbd>Volume UP</kbd> + <kbd>S</kbd>.
- Run `pip install -U lightnovel-crawler` again to install the latest updates.

### A4. Pydroid 3 (Android)

📱 Alternative to easy Termux is Pydroid3. It is a bit faster but harder to use and no _run-in-backgroud_ support.

- Install [Pydriod 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) from playstore.
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

### A5. Chatbots

#### A5.1 Telegram

Visit this link to get started with the telegram bot:
https://t.me/epub_smelter_bot

#### A5.2 Discord

Join our server: https://discord.gg/7A5Hktx

Or, visit this link to install discord bot to your own server:
https://discordapp.com/oauth2/authorize?client_id=537526751170002946&permissions=51264&scope=bot

Send `!help` to open the bot help message.

### A6. Run from source

- First clone the repository:

```bash
$ git clone https://github.com/dipu-bd/lightnovel-crawler
```

- Open command prompt inside of the project folder and install requirements:

```bash
$ pip install --user -r requirements.txt
```

- Run the program (use python v3.5 or higher):

```bash
$ python __main__.py

# Or, in short,
$ python .
```

### A7. Heroku Deployment

Simply fill out the environment variables and you get a running instance.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## (B) General Usage

### B1. Available options

To view list of available options:

```bash
$ lncrawl -h
================================================================================
                           📒 Lightnovel Crawler 🍀2.16.0
                  https://github.com/dipu-bd/lightnovel-crawler
--------------------------------------------------------------------------------
usage: lncrawl [options...]
       lightnovel-crawler [options...]

optional arguments:
  -h, --help            show this help message and exit

  -v, --version         show program's version number and exit
  -l                    Set log levels. (-l = warn, -ll = info, -lll = debug).
  --list-sources        Display a list of available sources.
  -s URL, --source URL  Profile page url of the novel.
  -f, --force           Force replace any existing folder.
  -i, --ignore          Ignore any existing folder (do not replace).
  --login USER PASSWD.  User name/email address and password for login.
  --all                 Download all chapters.
  --first [COUNT]       Download first few chapters (default: 10).
  --last [COUNT]        Download last few chapters (default: 10).
  --page START STOP.    The start and final chapter urls.
  --range FROM TO.      The start and final chapter indexes.
  --volumes [N [N ...]]
                        The list of volume numbers to download.
  --chapters [URL [URL ...]]
                        A list of specific chapter urls.
  --bot {console,telegram,discord,test}
                        Select a bot. Default: console.
  --suppress            Suppress all input prompts and use defaults.
  ENV                   [chatbots only] Pass query string at the end of all
                        options. It will be use instead of .env file. Sample:
                        "BOT=discord&DISCORD_TOKEN=***&LOG_LEVEL=DEBUG"

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

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose).

The list of currently available sources are given below:

| Available Sources                      | Search Enable |
| -------------------------------------- | :-----------: |
| http://gravitytales.com                |               |
| http://novelfull.com                   |       ✔       |
| http://www.machinenoveltranslation.com |               |
| http://zenithnovels.com                |               |
| https://anythingnovel.com              |               |
| https://babelnovel.com                 |       ✔       |
| https://bestlightnovel.com             |       ✔       |
| https://book.qidian.com                |               |
| https://boxnovel.com                   |       ✔       |
| https://creativenovels.com             |               |
| https://crescentmoon.blog              |               |
| https://id.mtlnovel.com                |       ✔       |
| https://kisslightnovels.info           |       ✔       |
| https://light-novel.online             |       ✔       |
| https://litnet.com                     |       ✔       |
| https://lnmtl.com                      |               |
| https://m.chinesefantasynovels.com     |               |
| https://m.novelspread.com              |               |
| https://m.romanticlovebooks.com        |               |
| https://m.wuxiaworld.co                |       ✔       |
| https://meionovel.com                  |               |
| https://mtled-novels.com               |       ✔       |
| https://myoniyonitranslations.com      |               |
| https://novelonlinefull.com            |       ✔       |
| https://novelplanet.com                |       ✔       |
| https://novelraw.blogspot.com          |               |
| https://volarenovels.com               |               |
| https://webnovel.online                |               |
| https://wordexcerpt.com/               |               |
| https://wuxiaworld.online              |       ✔       |
| https://www.asianhobbyist.com          |               |
| https://www.idqidian.us                |               |
| https://www.jieruihao.cn               |               |
| https://www.machine-translation.org    |       ✔       |
| https://www.mtlnovel.com               |       ✔       |
| https://www.novelall.com               |       ✔       |
| https://www.novelspread.com            |               |
| https://www.qidian.com                 |               |
| https://www.readlightnovel.org         |               |
| https://www.readnovelfull.com          |       ✔       |
| https://www.rebirth.online             |               |
| https://www.romanticlovebooks.com      |               |
| https://www.royalroad.com              |       ✔       |
| https://www.scribblehub.com            |       ✔       |
| https://www.shinsori.com               |               |
| https://www.tapread.com                |               |
| https://www.translateindo.com          |               |
| https://www.wattpad.com                |               |
| https://www.webnovel.com               |       ✔       |
| https://www.worldnovel.online          |       ✔       |
| https://www.wuxiaworld.co              |       ✔       |
| https://www.wuxiaworld.com             |       ✔       |

### C4. Rejected sources

| Rejected Sources              | Reason                              |
| ----------------------------- | ----------------------------------- |
| http://fullnovel.live         | `403 - Forbidden: Access is denied` |
| http://moonbunnycafe.com      | `Does not follow uniform format`    |
| https://4scanlation.xyz       | `Domain expired`                    |
| https://comrademao.com        | `Removed`                           |
| https://indomtl.com           | `Does not like to be crawled`       |
| https://lnindo.org            | `Does not like to be crawled`       |
| https://novelgo.id/           | `Removed`                           |
| https://www.noveluniverse.com | `Site is down`                      |
| https://www.novelupdates.com  | `Does not host any novels`          |
| https://www.novelv.com        | `Site is down`                      |
| https://yukinovel.id          | `Removed`                           |

### C5. Supported output formats

When download is done, the following files can be generated:

- [x] JSON (default)
- [x] TEXT
- [x] WEB
- [x] EPUB
- [x] DOCX
- [x] MOBI
- [x] PDF
- [x] RTF
- [x] TXT
- [x] AZW3
- [x] FB2
- [x] LIT
- [x] LRF
- [x] OEB
- [x] PDB
- [x] PML
- [x] RB
- [x] SNB
- [x] TCR
- [x] HTML

### C6. Supported bots

- [x] Console Bot
- [x] Telegram Bot
- [x] Discord Bot

## (D) The project structure

[Click here](https://github.com/dipu-bd/lightnovel-crawler/blob/master/CONTRIBUTING.md) to view details.
