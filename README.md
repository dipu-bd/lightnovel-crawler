# Lightnovel Crawler

[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg?logo=python)](https://pypi.org/project/lightnovel-crawler)
[![download win](https://img.shields.io/badge/download-lncrawl.exe-red?logo=windows)](https://rebrand.ly/lncrawl)
[![download linux](https://img.shields.io/badge/download-lncrawl_(linux)-brown?logo=linux)](https://rebrand.ly/lncrawl-linux)
[![Discord](https://img.shields.io/discord/578550900231110656?logo=discord&label=discord)](https://discord.gg/wMECG2Q)
<br>
[![Build and Publish](https://github.com/dipu-bd/lightnovel-crawler/actions/workflows/release.yml/badge.svg)](https://github.com/dipu-bd/lightnovel-crawler/actions/workflows/release.yml)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dipu-bd/lightnovel-crawler?logo=github)](https://github.com/dipu-bd/lightnovel-crawler)

<!-- [![AppVeyor](https://img.shields.io/appveyor/build/dipu-bd/lightnovel-crawler?logo=appveyor)](https://ci.appveyor.com/project/dipu-bd/lightnovel-crawler) -->
<!-- [![travis-ci](https://travis-ci.com/dipu-bd/lightnovel-crawler.svg?branch=master)](https://travis-ci.com/dipu-bd/lightnovel-crawler) -->
<!-- [![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler) -->

An app to download novels from online sources and generate e-books.

> **Discord: [https://discord.gg/wMECG2Q](https://discord.gg/wMECG2Q)** 

> **Telegram: [https://t.me/epub_smelter_bot](https://t.me/epub_smelter_bot)**

## Table of contents

- [Lightnovel Crawler](#lightnovel-crawler)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
    - [Standalone Bundle (Windows, Linux)](#standalone-bundle-windows-linux)
    - [PIP (Windows, Mac, and Linux)](#pip-windows-mac-and-linux)
    - [Termux (Android)](#termux-android)
    - [Chatbots](#chatbots)
      - [Discord](#discord)
      - [Telegram](#telegram)
    - [Heroku Deployment](#heroku-deployment)
  - [Running from source](#running-from-source)
  - [Running the Bots](#running-the-bots)
  - [General Usage](#general-usage)
    - [Available options](#available-options)
    - [Example Usage](#example-usage)
  - [Development](#development)
    - [Adding new source](#adding-new-source)
    - [Adding new Bot](#adding-new-bot)
    - [Supported sources](#supported-sources)
    - [Rejected sources](#rejected-sources)
    - [Supported output formats](#supported-output-formats)
    - [Supported bots](#supported-bots)

<a href="https://github.com/dipu-bd/lightnovel-crawler"><img src="res/lncrawl-icon.png" width="128px" align="right"/></a>

## Installation

**This application uses _Calibre_ to convert ebooks.** <br>
**Install it from https://calibre-ebook.com/download** <br>
Without it, you will only get output in epub, text, and web formats.

<!-- Also, you have to install **node.js** to access cloudflare enabled sites (e.g. https://novelplanet.com/). Download and install node.js from here: https://nodejs.org/en/download/ -->

### Standalone Bundle (Windows, Linux)

⏬ **Windows**: [lncrawl.exe ~ 25MB](https://rebrand.ly/lncrawl)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program.

⏬ **Linux**: [lncrawl ~ 30MB](https://rebrand.ly/lncrawl-linux)

> It is recommended to install via **pip** if you are on Linux

⏬ _To get older versions visit the [Releases page](https://github.com/dipu-bd/lightnovel-crawler/releases)_

### PIP (Windows, Mac, and Linux)

📦 A python package named `lightnovel-crawler` is available at [pypi](https://pypi.org/project/lightnovel-crawler).

> Make sure you have installed **Python** v3.6 or higher and have **pip** enabled. Visit these links to install python with pip in [Windows](https://stackoverflow.com/a/44437176/1583052), [Linux](https://stackoverflow.com/a/51799221/1583052) and [MacOS](https://itsevans.com/install-pip-osx/). Feel free to ask on the Discord server if you are stuck.

To install this app or to update installed one via `pip`, just run:

```bash
$ pip install --user -U lightnovel-crawler
```

In some cases you have to use `python3 -m pip` or `pip3` or `python -m pip`. And you do not need `--user` option, if you are running from root.

Next, open your terminal and enter:

```bash
$ lightnovel-crawler

# Or, a shortcut:
$ lncrawl
```

> To view extra logs, use: `lncrawl -lll`

### Termux (Android)

> There is no official support to run python in mobile devices.
> It is not guaranteed that the app will run smoothly in all devices.
> It is recommended to use the bots on either Discord or Telegram if you are on mobile.

📱 Using Termux, you can run this app in your android phones too. Follow this instructions:

- Install [Termux](https://play.google.com/store/apps/details?id=com.termux) from playstore.
- Open the app and run these commands one by one:
  - `apt update && apt upgrade`
  - `termux-setup-storage`
  - `pkg install ndk-sysroot make python zlib clang`
  - `pkg install libxml2 libxslt libiconv libcrypt libffi zlib libjpeg-turbo`
  - `pip install -U lightnovel-crawler` to install the latest version of this app.
- Now exit the console and relaunch it.
- Type `cd ~/storage/downloads` to store novels there.
- Type `lncrawl` to start.
- You can navigate up using <kbd>Volume UP</kbd> + <kbd>W</kbd> and down using <kbd>Volume UP</kbd> + <kbd>S</kbd>.

When there is a new update available, you can install it just by running `pip install -U lightnovel-crawler`. You will not have to run all the above commands again.

### Chatbots

#### Discord

Join our server: https://discord.gg/7A5Hktx

Or, visit this link to install discord bot to your own server:
https://discordapp.com/oauth2/authorize?client_id=537526751170002946&permissions=51264&scope=bot

#### Telegram

Visit this link to get started with the telegram bot:
https://t.me/epub_smelter_bot

Send `!help` to open the bot help message.

### Heroku Deployment

Simply fill out the environment variables and you get a running instance.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Running from source

- First clone the repository:

```bash
$ git clone https://github.com/dipu-bd/lightnovel-crawler
```

- Open command prompt inside of the project folder and install requirements:

```bash
$ pip install --user -r requirements.txt
```

- Run the program (use python v3.6 or higher):

```bash
$ python __main__.py

# Or, in short,
$ python .
```

## Running the Bots

There are two chatbots available at this moment: Telegram and Discord. To run your own bot server, follow these instructions:

- Clone this repository
```bash
$ git clone https://github.com/dipu-bd/lightnovel-crawler
```

- Install calibre for pdf, mobi etc. formats.
  - https://calibre-ebook.com/download

- Install requirements
```bash
$ pip3 install --user -r requirements.txt
```

- Copy `.env.example` file to `.env` file. Edit this file and give your API credentials here.

- To run the discord bot:
```bash
$ python3 . --bot discord --shard-id 0 --shard-count 1
```

- To run the telegram bot
```bash
$ python3 . --bot telegram
```

_There is a `start.sh` script to run a bot in ubuntu servers. It will basically execute the `python __main__.py` and send the task to run in background. I use it to run my discord bot in the server._

## General Usage

### Available options

```bash
$ lncrawl -h
================================================================================
╭╮╱╱╱╱╱╱╭╮╱╭╮╱╱╱╱╱╱╱╱╱╱╱╱╭╮╱╭━━━╮╱╱╱╱╱╱╱╱╱╭╮
┃┃╱╱╱╱╱╱┃┃╭╯╰╮╱╱╱╱╱╱╱╱╱╱╱┃┃╱┃╭━╮┃╱╱╱╱╱╱╱╱╱┃┃
┃┃╱╱╭┳━━┫╰┻╮╭╋━╮╭━━┳╮╭┳━━┫┃╱┃┃╱╰╋━┳━━┳╮╭╮╭┫┃╭━━┳━╮
┃┃╱╭╋┫╭╮┃╭╮┃┃┃╭╮┫╭╮┃╰╯┃┃━┫┃╱┃┃╱╭┫╭┫╭╮┃╰╯╰╯┃┃┃┃━┫╭╯
┃╰━╯┃┃╰╯┃┃┃┃╰┫┃┃┃╰╯┣╮╭┫┃━┫╰╮┃╰━╯┃┃┃╭╮┣╮╭╮╭┫╰┫┃━┫┃
╰━━━┻┻━╮┣╯╰┻━┻╯╰┻━━╯╰╯╰━━┻━╯╰━━━┻╯╰╯╰╯╰╯╰╯╰━┻━━┻╯
╱╱╱╱╱╭━╯┃ v2.27.2
╱╱╱╱╱╰━━╯ 🔗 https://github.com/dipu-bd/lightnovel-crawler
--------------------------------------------------------------------------------
usage: lncrawl [options...]
       lightnovel-crawler [options...]

optional arguments:
  -h, --help            show this help message and exit

  -v, --version         show program's version number and exit
  -l                    Set log levels. (-l = warn, -ll = info, -lll = debug).
  --list-sources        Display a list of available sources.
  --crawler [FILES [FILES ...]]
                        Load additional crawler files.
  -s URL, --source URL  Profile page url of the novel.
  -q STR, --query STR   Novel query followed by list of source sites.
  -x [REGEX], --sources [REGEX]
                        Filter out the sources to search for novels.
  --login USER PASSWD   User name/email address and password for login.
  --format E [E ...]    Define which formats to output. Default: all.
  --add-source-url      Add source url at the end of each chapter.
  --single              Put everything in a single book.
  --multi               Build separate books by volumes.
  -o PATH, --output PATH
                        Path where the downloads to be stored.
  --filename NAME       Set the output file name
  --filename-only       Skip appending chapter range with file name
  -f, --force           Force replace any existing folder.
  -i, --ignore          Ignore any existing folder (do not replace).
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
  --shard-id [SHARD_ID]
                        Discord bot shard id (default: 0)
  --shard-count [SHARD_COUNT]
                        Discord bot shard counts (default: 1)
  --suppress            Suppress all input prompts and use defaults.
  --resume [NAME/URL]   Resume download of a novel containing in /home/dipu/projects/lightnovel-crawler/Lightnovels
  ENV                   [chatbots only] Pass query string at the end of all options. It will be use instead of .env file. Sample: "BOT=discord&DISCORD_TOKEN=***&LOG_LEVEL=DEBUG"

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

### Example Usage

Open your console and type `lncrawl --version` first to check if you have installed it properly.
Here are some example usage of the app:

- To start an interactive session: `lncrawl`

- To download using an url: `lncrawl -s https://boxnovel.com/novel/reincarnation-of-the-strongest-sword-god/`
- To search novels: `lncrawl -q "Strongest Sword God"`
- To search novels from selected sources: `lncrawl -q "Strongest Sword God" --sources`

- To download all chapters: `lncrawl --all`
- To download first 25 chapters: `lncrawl --first 25`
- To download all between two chapters: `lncrawl --range 10 30`
- To download all between two chapter links: `lncrawl -s https://novelfull.com/release-that-witch.html --chapters https://novelfull.com/release-that-witch/chapter-6-training-part-i.html https://novelfull.com/release-that-witch/chapter-8-months-of-the-demons-part-1.html`
- To download a specific volumes: `lncrawl --volumes 2 3`

- To define output path: `lncrawl -o "D:\Lightnovels\reincarnation-of-the-strongest-sword-god"`
- To delete the output folder if exists: `lncrawl -f`
- To ignore the output folder if exists: `lncrawl -i`
- To resume download where is has been left previously: `lncrawl -i`
- To specify output formats: `lncrawl --format epub pdf mobi`

- To display list of supported sources: `lncrawl --list-sources`

- If you provide an option in the argument, it will skip it in the interactive session.
  If you want to disable all interactive prompts, pass `--suppress` at the end.

- You can stack up options like this: `lncrawl -s https://boxnovel.com/novel/reincarnation-of-the-strongest-sword-god/ -o "D:\Lightnovels\reincarnation-of-the-strongest-sword-god" --last 50 -i --format pdf --suppress`

## Development

You are very welcome to contribute in this project. You can:

- create new issues pointing out the bugs.
- solve existing issues.
- add your own sources.
- add new output formats.
- create new bots.

### Adding new source

- Create new crawler using the [`sources/_template_.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/sources/_template_.py) as template.
- Update [Supported sources](#c3-supported-sources) section in `README.md`
- Add some test inputs to `test_user_inputs` variable in `lncrawl/bots/test/test_inputs.py`

### Adding new Bot

- Create a new bot file using [`bots/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/_sample.py) as template.
- Import bot to [`bots/__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/__init__.py) file.

### Supported sources

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose).

| Available Sources                            | Can Search | Can Login |      Maintainer       |
| -------------------------------------------- | :--------: | :-------: | :-------------------: |
| http://boxnovel.cloud                        |     ✔      |           |      @SirGryphin      |
| http://boxnovel.org                          |     ✔      |           |       @dipu-bd        |
| http://hs2ppe.co.uk                          |     ✔      |           |      @SirGryphin      |
| http://liberspark.com                        |            |           |       @dipu-bd        |
| http://novelfull.com                         |     ✔      |           |       @dipu-bd        |
| http://novels.cloud                          |     ✔      |           |      @SirGryphin      |
| http://readonlinenovels.com                  |            |           |       @dipu-bd        |
| http://tiknovel.com                          |            |           |       @dipu-bd        |
| http://wspadancewichita.com                  |     ✔      |           |      @SirGryphin      |
| http://wuxiaworld.cloud                      |     ✔      |           |      @SirGryphin      |
| http://www.fujitranslation.com               |            |           |       @dipu-bd        |
| http://www.hanyunovels.site                  |     ✔      |           |      @SirGryphin      |
| http://www.machinenoveltranslation.com       |            |           |       @dipu-bd        |
| http://www.tiknovel.com                      |            |           |       @dipu-bd        |
| http://zenithnovels.com                      |            |           |       @dipu-bd        |
| http://zhi-end.blogspot.co.id                |            |           |      @SirGryphin      |
| http://zhi-end.blogspot.com                  |            |           |      @SirGryphin      |
| https://1stkissnovel.love                    |     ✔      |           |      @SirGryphin      |
| https://88tangeatdrinkread.wordpress.com     |            |           |      @SirGryphin      |
| https://9kqw.com                             |     ✔      |           |       @dipu-bd        |
| https://allnovel.org                         |     ✔      |           |      @SirGryphin      |
| https://amnesiactl.com                       |            |           |      @SirGryphin      |
| https://anonanemone.wordpress.com            |            |           |      @SirGryphin      |
| https://arangscans.com                       |            |           |      @SirGryphin      |
| https://arnovel.me                           |     ✔      |           |      @SirGryphin      |
| https://asadatranslations.com                |     ✔      |           |      @SirGryphin      |
| https://automtl.wordpress.com                |            |           |      @SirGryphin      |
| https://babelnovel.com                       |     ✔      |     ✔     |       @dipu-bd        |
| https://bestlightnovel.com                   |     ✔      |           |       @dipu-bd        |
| https://book.qidian.com                      |            |           |       @dipu-bd        |
| https://booknet.com                          |            |           | @dipu-bd, @SirGryphin |
| https://boxnovel.com                         |     ✔      |           |       @dipu-bd        |
| https://boxnovel.online                      |     ✔      |           |      @SirGryphin      |
| https://cclawtranslations.home.blog          |            |           |      @SirGryphin      |
| https://clicknovel.net                       |            |           |      @SirGryphin      |
| https://creativenovels.com                   |            |           |       @dipu-bd        |
| https://crescentmoon.blog                    |            |           |       @dipu-bd        |
| https://daonovel.com                         |     ✔      |           |      @SirGryphin      |
| https://darktranslation.com                  |            |           |      @SirGryphin      |
| https://demontranslations.com                |            |           |      @SirGryphin      |
| https://dmtranslationscn.com                 |            |           |      @SirGryphin      |
| https://dobelyuwai.wordpress.com             |            |           |      @SirGryphin      |
| https://docln.net                            |     ✔      |           |       @dipu-bd        |
| https://dsrealmtranslations.com              |            |           |      @SirGryphin      |
| https://es.mtlnovel.com                      |     ✔      |           |       @dipu-bd        |
| https://exiledrebelsscanlations.com          |            |           |      @SirGryphin      |
| https://fanstranslations.com                 |            |           |      @SirGryphin      |
| https://fastnovel.net                        |     ✔      |           |      @SirGryphin      |
| https://fr.mtlnovel.com                      |     ✔      |           |       @dipu-bd        |
| https://fujitranslation.com                  |            |           |      @SirGryphin      |
| https://grensia.blogspot.com                 |            |           |       @dipu-bd        |
| https://hui3r.wordpress.com                  |            |           |      @SirGryphin      |
| https://id.mtlnovel.com                      |     ✔      |           |       @dipu-bd        |
| https://inadequatetranslations.wordpress.com |            |           |      @SirGryphin      |
| https://indowebnovel.id                      |            |           |       @dipu-bd        |
| https://infinitenoveltranslations.net        |            |           |      @SirGryphin      |
| https://instadoses.com                       |            |           |       @dipu-bd        |
| https://isotls.com                           |            |           |      @SirGryphin      |
| https://jpmtl.com                            |            |           |       @dipu-bd        |
| https://jstranslations1.com                  |            |           |      @SirGryphin      |
| https://justatranslatortranslations.com      |            |           |      @SirGryphin      |
| https://kiss-novel.com                       |            |           |       @dipu-bd        |
| https://kisslightnovels.info                 |     ✔      |           |       @dipu-bd        |
| https://lazybirdtranslations.wordpress.com   |            |           |      @SirGryphin      |
| https://lemontreetranslations.wordpress.com  |            |           |      @SirGryphin      |
| https://light-novel.online                   |     ✔      |           |       @dipu-bd        |
| https://lightnovel.tv                        |     ✔      |           |      @SirGryphin      |
| https://lightnovel.world                     |            |           |      @SirGryphin      |
| https://lightnovelbastion.com                |            |           |       @dipu-bd        |
| https://lightnovelheaven.com                 |            |           |      @SirGryphin      |
| https://lightnovelkiss.com                   |     ✔      |           |      @SirGryphin      |
| https://lightnovelshub.com                   |     ✔      |           |      @SirGryphin      |
| https://lightnovelsonl.com                   |     ✔      |           |      @SirGryphin      |
| https://lightnovelstranslations.com          |            |           |      @SirGryphin      |
| https://listnovel.com                        |     ✔      |           |       @dipu-bd        |
| https://litnet.com                           |            |           |       @dipu-bd        |
| https://ln.hako.re                           |     ✔      |           |       @dipu-bd        |
| https://lnmtl.com                            |            |     ✔     |       @dipu-bd        |
| https://m.chinesefantasynovels.com           |            |           |       @dipu-bd        |
| https://m.mywuxiaworld.com                   |     ✔      |           |       @dipu-bd        |
| https://m.novelspread.com                    |            |           |       @dipu-bd        |
| https://m.readlightnovel.cc                  |            |           |       @dipu-bd        |
| https://m.romanticlovebooks.com              |            |           |       @dipu-bd        |
| https://m.wuxiaworld.co                      |     ✔      |           |       @dipu-bd        |
| https://mangatoon.mobi                       |            |           |       @dipu-bd        |
| https://meionovel.id                         |     ✔      |           |       @dipu-bd        |
| https://moonstonetranslation.com             |            |           |      @SirGryphin      |
| https://morenovel.net                        |     ✔      |           |      @SirGryphin      |
| https://myoniyonitranslations.com            |            |           |       @dipu-bd        |
| https://mysticalmerries.com                  |     ✔      |           |      @SirGryphin      |
| https://newsite.kolnovel.com                 |     ✔      |           |      @SirGryphin      |
| https://novel27.com                          |     ✔      |           |      @SirGryphin      |
| https://novelcake.com                        |     ✔      |           |      @SirGryphin      |
| https://novelcrush.com                       |     ✔      |           |      @SirGryphin      |
| https://novelextra.com                       |     ✔      |           |      @SirGryphin      |
| https://novelfull.com                        |     ✔      |           |       @dipu-bd        |
| https://novelfullplus.com                    |     ✔      |           | @dipu-bd, @SirGryphin |
| https://novelgate.net                        |     ✔      |           |      @SirGryphin      |
| https://novelgo.id/                          |            |           |       @dipu-bd        |
| https://novelmic.com                         |     ✔      |           |      @SirGryphin      |
| https://novelonlinefree.com                  |     ✔      |           |      @SirGryphin      |
| https://novelonlinefull.com                  |     ✔      |           |       @dipu-bd        |
| https://novelraw.blogspot.com                |            |           |       @dipu-bd        |
| https://novels.pl                            |            |           |       @dipu-bd        |
| https://novelsite.net                        |     ✔      |           |      @SirGryphin      |
| https://novelsonline.net                     |            |           |      @SirGryphin      |
| https://novelsrock.com                       |            |           |       @dipu-bd        |
| https://noveltoon.mobi/                      |     ✔      |           |       @dipu-bd        |
| https://noveltranslate.com                   |     ✔      |           |      @SirGryphin      |
| https://noveltrench.com                      |     ✔      |           |      @SirGryphin      |
| https://omgnovels.com                        |     ✔      |           |      @SirGryphin      |
| https://overabook.com                        |     ✔      |           |      @SirGryphin      |
| https://ranobelib.me                         |            |           |       @dipu-bd        |
| https://ranobes.net                          |            |           |       @dipu-bd        |
| https://readlightnovels.net                  |     ✔      |           |     @PreownedFIN      |
| https://readnovelz.net                       |     ✔      |           |      @SirGryphin      |
| https://readwebnovels.net                    |     ✔      |           |      @SirGryphin      |
| https://reincarnationpalace.com              |            |           |      @SirGryphin      |
| https://rewayat.club                         |            |           |       @dipu-bd        |
| https://rpgnoob.wordpress.com                |            |           |      @SirGryphin      |
| https://rpgnovels.com                        |            |           |      @SirGryphin      |
| https://shalvationtranslations.wordpress.com |            |           |      @SirGryphin      |
| https://skynovel.org/                        |            |           |      @SirGryphin      |
| https://sleepytranslations.com               |            |           |      @SirGryphin      |
| https://smnovels.com                         |            |           |      @SirGryphin      |
| https://steambunlightnovel.com               |            |           |      @SirGryphin      |
| https://supernovel.net                       |     ✔      |           |      @SirGryphin      |
| https://toc.qidianunderground.org            |     ✔      |           |       @dipu-bd        |
| https://tomotranslations.com                 |            |           |       @dipu-bd        |
| https://totallytranslations.com              |            |           | @SirGryphin, @dipu-bd |
| https://tunovelaligera.com                   |     ✔      |           |      @SirGryphin      |
| https://viewnovel.net                        |     ✔      |           |      @SirGryphin      |
| https://vipnovel.com                         |     ✔      |           |      @SirGryphin      |
| https://vistranslations.wordpress.com        |            |           |      @SirGryphin      |
| https://volarenovels.com                     |            |           |       @dipu-bd        |
| https://wbnovel.com                          |     ✔      |           |       @dipu-bd        |
| https://webnovel.online                      |            |           |       @dipu-bd        |
| https://webnovelindonesia.com                |            |           |       @dipu-bd        |
| https://webnovelonline.com                   |            |           |       @dipu-bd        |
| https://wondernovels.com                     |     ✔      |           |      @SirGryphin      |
| https://woopread.com                         |     ✔      |           |       @dipu-bd        |
| https://wordexcerpt.com                      |     ✔      |           | @dipu-bd, @SirGryphin |
| https://wordexcerpt.org                      |            |           | @dipu-bd, @SirGryphin |
| https://wujizun.com                          |            |           |      @SirGryphin      |
| https://wuxiaworld.io                        |     ✔      |           |      @SirGryphin      |
| https://wuxiaworld.live                      |     ✔      |           |      @SirGryphin      |
| https://wuxiaworld.name                      |     ✔      |           |      @SirGryphin      |
| https://wuxiaworld.online                    |     ✔      |           |       @dipu-bd        |
| https://wuxiaworld.site                      |            |           |       @dipu-bd        |
| https://wuxiaworldsite.co                    |            |           |       @dipu-bd        |
| https://www.1ksy.com                         |            |           |      @SirGryphin      |
| https://www.aixdzs.com                       |            |           |       @dipu-bd        |
| https://www.asianhobbyist.com                |            |           |       @dipu-bd        |
| https://www.box-novel.com                    |     ✔      |           |      @SirGryphin      |
| https://www.daocaorenshuwu.com               |            |           |      @SirGryphin      |
| https://www.f-w-o.com                        |     ✔      |           |      @SirGryphin      |
| https://www.flying-lines.com                 |            |           |       @dipu-bd        |
| https://www.foxaholic.com                    |     ✔      |           |      @SirGryphin      |
| https://www.foxteller.com                    |     ✔      |           |       @dipu-bd        |
| https://www.freelightnovel.com               |            |           |      @SirGryphin      |
| https://www.fuyuneko.org                     |            |           |      @SirGryphin      |
| https://www.idqidian.us                      |            |           |       @dipu-bd        |
| https://www.koreanmtl.online                 |            |           |       @dipu-bd        |
| https://www.lightnovelpub.com                |     ✔      |           |       @dipu-bd        |
| https://www.lunarletters.com                 |            |           |      @SirGryphin      |
| https://www.machine-translation.org          |     ✔      |           |       @dipu-bd        |
| https://www.miraslation.net                  |            |           |      @SirGryphin      |
| https://www.mtlnovel.com                     |     ✔      |           |       @dipu-bd        |
| https://www.mywuxiaworld.com                 |     ✔      |           |       @dipu-bd        |
| https://www.novelall.com                     |     ✔      |           |       @dipu-bd        |
| https://www.novelcool.com                    |            |           |      @SirGryphin      |
| https://www.novelhall.com                    |            |           |       @dipu-bd        |
| https://www.novelhunters.com                 |     ✔      |           |      @SirGryphin      |
| https://www.novelmultiverse.com              |     ✔      |           |      @SirGryphin      |
| https://www.novelpassion.com                 |     ✔      |           |      @SirGryphin      |
| https://www.novelringan.com                  |            |           |       @dipu-bd        |
| https://www.novels.pl                        |            |           |       @dipu-bd        |
| https://www.novelspread.com                  |            |           |       @dipu-bd        |
| https://www.novelupdates.cc                  |            |           |      @SirGryphin      |
| https://www.oppatranslations.com             |            |           |      @SirGryphin      |
| https://www.ornovel.com                      |            |           |      @SirGryphin      |
| https://www.qidian.com                       |            |           |       @dipu-bd        |
| https://www.readlightnovel.cc                |            |           |       @dipu-bd        |
| https://www.readlightnovel.org               |            |           |       @dipu-bd        |
| https://www.readnovelfull.com                |     ✔      |           |       @dipu-bd        |
| https://www.readwn.com/                      |     ✔      |           |       @dipu-bd        |
| https://www.romanticlovebooks.com            |            |           |       @dipu-bd        |
| https://www.royalroad.com                    |     ✔      |           |       @dipu-bd        |
| https://www.scribblehub.com                  |     ✔      |           |       @dipu-bd        |
| https://www.shinsori.com                     |            |           |       @dipu-bd        |
| https://www.tapread.com                      |            |           |       @dipu-bd        |
| https://www.translateindo.com                |            |           |       @dipu-bd        |
| https://www.virlyce.com                      |            |           |      @SirGryphin      |
| https://www.wattpad.com                      |            |           |       @dipu-bd        |
| https://www.webnovel.com                     |     ✔      |           |       @dipu-bd        |
| https://www.webnovelover.com                 |     ✔      |           |      @SirGryphin      |
| https://www.wnmtl.org                        |            |           |      @SirGryphin      |
| https://www.worldnovel.online                |     ✔      |           |       @dipu-bd        |
| https://www.wuxialeague.com                  |            |           |       @dipu-bd        |
| https://www.wuxiaworld.co                    |     ✔      |           |       @dipu-bd        |
| https://www.wuxiaworld.com                   |     ✔      |           |       @dipu-bd        |
| https://www.x81zw.com                        |            |           |      @SirGryphin      |
| https://www.xiainovel.com                    |            |           |      @SirGryphin      |
| https://www.xsbiquge.com                     |            |           |      @SirGryphin      |
| https://yukinovel.id                         |            |           |       @dipu-bd        |
| https://zinnovel.com                         |     ✔      |           |      @SirGryphin      |

### Rejected sources

| Rejected Sources                | Reason                                                                                             |
| ------------------------------- | -------------------------------------------------------------------------------------------------- |
| http://fullnovel.live           | `This site can’t be reached`                                                                |
| http://gravitytales.com         | `Redirects to webnovel.com`                                                                        |
| http://moonbunnycafe.com        | `Does not follow uniform format`                                                                   |
| https://4scanlation.xyz         | `Site moved`                                                                                       |
| https://anythingnovel.com       | `Site broken`                                                                                      |
| https://bestoflightnovels.com   | `Site moved`                                                                                       |
| https://chrysanthemumgarden.com | `Removed on request of the owner` [#649](https://github.com/dipu-bd/lightnovel-crawler/issues/649) |
| https://fsapk.com               | `Site is not working`                                                                              |
| https://indomtl.com             | `Does not like to be crawled`                                                                      |
| https://lnindo.org              | `Does not like to be crawled`                                                                      |
| https://mtled-novels.com        | `Domain is expired`                                                                                |
| https://novelcrush.com          | `Site is down`                                                                                     |
| https://novelplanet.com         | `Site is closed`                                                                                   |
| https://pery.info               | `Site is down`                                                                                     |
| https://writerupdates.com       | `Site is down`                                                                                     |
| https://www.centinni.com        | `Site is down`                                                                                     |
| https://www.hotmtlnovel.xyz     | `Cloudflare version 2 challenge`                                                                   |
| https://www.jieruihao.cn        | `Unavailable`                                                                                      |
| https://www.noveluniverse.com   | `Site is down`                                                                                     |
| https://www.novelupdates.com    | `Does not host any novels`                                                                         |
| https://www.novelv.com          | `Site is down`                                                                                     |
| https://www.rebirth.online      | `Site moved`                                                                                       |

### Supported output formats

- JSON
- EPUB
- TEXT
- WEB
- DOCX
- MOBI
- PDF
- RTF
- TXT
- AZW3
- FB2
- LIT
- LRF
- OEB
- PDB
- PML
- RB
- SNB
- TCR
- HTML

### Supported bots

- Console Bot
- Telegram Bot
- Discord Bot
