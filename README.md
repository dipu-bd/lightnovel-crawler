# Lightnovel Crawler

[![download win](https://img.shields.io/badge/download-lncrawl.exe-red?logo=windows)](https://rebrand.ly/lncrawl)
[![download linux](<https://img.shields.io/badge/download-lncrawl_(linux)-brown?logo=linux>)](https://rebrand.ly/lncrawl-linux)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg?logo=python)](https://pypi.org/project/lightnovel-crawler)
<br>
[![Build and Publish](https://github.com/dipu-bd/lightnovel-crawler/actions/workflows/release.yml/badge.svg)](https://github.com/dipu-bd/lightnovel-crawler/actions/workflows/release.yml)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dipu-bd/lightnovel-crawler?logo=github)](https://github.com/dipu-bd/lightnovel-crawler)
[![Discord](https://img.shields.io/discord/578550900231110656?logo=discord&label=discord)](https://discord.gg/wMECG2Q)

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
$ python lncrawl
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
$ python3 lncrawl --bot discord --shard-id 0 --shard-count 1
```

- To run the telegram bot

```bash
$ python3 lncrawl --bot telegram
```

_There is a `start.sh` script to run a bot in ubuntu servers. It will basically execute the `python3 lncrawl` and send the task to run in background. I use it to run my discord bot in the server._

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

## Supported sources

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose).

<!-- auto generated supported sources list -->

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://boxnovel.cloud/" target="_blank">http://boxnovel.cloud/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/boxnovelcloud.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://boxnovel.org/" target="_blank">http://boxnovel.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/boxnovelorg.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://es.mtlnovel.com/" target="_blank">http://es.mtlnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mtlnovel.py">1627918840</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://fastnovel.net/" target="_blank">http://fastnovel.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fastnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://fr.mtlnovel.com/" target="_blank">http://fr.mtlnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mtlnovel.py">1627918840</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://hs2ppe.co.uk/" target="_blank">http://hs2ppe.co.uk/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/hs2ppe.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://id.mtlnovel.com/" target="_blank">http://id.mtlnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mtlnovel.py">1627918840</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://liberspark.com/" target="_blank">http://liberspark.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/liberspark.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://novelfull.com/" target="_blank">http://novelfull.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelfull.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://novels.cloud/" target="_blank">http://novels.cloud/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelscloud.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://readonlinenovels.com/" target="_blank">http://readonlinenovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readonlinenovels.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, amritoo, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://tiknovel.com/" target="_blank">http://tiknovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/tiknovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://wspadancewichita.com/" target="_blank">http://wspadancewichita.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wspadancewichita.py">1627433129</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://wuxiaworld.cloud/" target="_blank">http://wuxiaworld.cloud/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaworldcloud.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://www.fujitranslation.com/" target="_blank">http://www.fujitranslation.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fujitrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://www.hanyunovels.site/" target="_blank">http://www.hanyunovels.site/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/hanyunovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://www.indonovels.net/" target="_blank">http://www.indonovels.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/indonovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://www.machinenoveltranslation.com/" target="_blank">http://www.machinenoveltranslation.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/machinetrans.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="http://www.mtlnovel.com/" target="_blank">http://www.mtlnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mtlnovel.py">1627918840</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://www.tiknovel.com/" target="_blank">http://www.tiknovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/9kqw.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://zenithnovels.com/" target="_blank">http://zenithnovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/zenithnovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://zhi-end.blogspot.co.id/" target="_blank">http://zhi-end.blogspot.co.id/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/zhiend.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="http://zhi-end.blogspot.com/" target="_blank">http://zhi-end.blogspot.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/zhiend.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://1stkissnovel.love/" target="_blank">https://1stkissnovel.love/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/1stkissnovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki, mchubby</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://88tangeatdrinkread.wordpress.com/" target="_blank">https://88tangeatdrinkread.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/88tang.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://9kqw.com/" target="_blank">https://9kqw.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/9kqw.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://allnovel.org/" target="_blank">https://allnovel.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/allnovel.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://amnesiactl.com/" target="_blank">https://amnesiactl.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/amnesiactl.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://anonanemone.wordpress.com/" target="_blank">https://anonanemone.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/anonanemone.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://arangscans.com/" target="_blank">https://arangscans.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/arangscans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://arnovel.me/" target="_blank">https://arnovel.me/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/arnovel.py">1628469563</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://asadatranslations.com/" target="_blank">https://asadatranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/asadatrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://automtl.wordpress.com/" target="_blank">https://automtl.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/automtl.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login">🔑</span></td>
<td><a href="https://babelnovel.com/" target="_blank">https://babelnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/babelnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://bestlightnovel.com/" target="_blank">https://bestlightnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/bestlightnovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://book.qidian.com/" target="_blank">https://book.qidian.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/qidiancom.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://booknet.com/" target="_blank">https://booknet.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/booknet.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://boxnovel.com/" target="_blank">https://boxnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/boxnovel.py">1627279453</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://boxnovel.online/" target="_blank">https://boxnovel.online/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/boxnovelonline.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://cclawtranslations.home.blog/" target="_blank">https://cclawtranslations.home.blog/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/domentranslations.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://clicknovel.net/" target="_blank">https://clicknovel.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/clicknovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://comrademao.com/" target="_blank">https://comrademao.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fu_kemao.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://creativenovels.com/" target="_blank">https://creativenovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/creativenovels.py">1627423436</a></td>
<td><span class="font-size: 0.8em">Jonathan Lane, Sudipto Chandra, Sudipto Chandra Dipu, Tom James Butcher, Yudi Santoso, kuwoyuki, tidux, tomcb1</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://crescentmoon.blog/" target="_blank">https://crescentmoon.blog/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/crescentmoon.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://daonovel.com/" target="_blank">https://daonovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/daonovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://darktranslation.com/" target="_blank">https://darktranslation.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/darktrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://demontranslations.com/" target="_blank">https://demontranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/demontrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://dmtranslationscn.com/" target="_blank">https://dmtranslationscn.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/dmtrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://dobelyuwai.wordpress.com/" target="_blank">https://dobelyuwai.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/dobelyuwai.py">1628465042</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://docln.net/" target="_blank">https://docln.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lnhakone.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://domentranslations.wordpress.com/" target="_blank">https://domentranslations.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/domentranslations.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://exiledrebelsscanlations.com/" target="_blank">https://exiledrebelsscanlations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/exiledrebels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://fanstranslations.com/" target="_blank">https://fanstranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fanstrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://fujitranslation.com/" target="_blank">https://fujitranslation.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fujitrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://grensia.blogspot.com/" target="_blank">https://grensia.blogspot.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/grensia_blogspot.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://hui3r.wordpress.com/" target="_blank">https://hui3r.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/hui3r.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://inadequatetranslations.wordpress.com/" target="_blank">https://inadequatetranslations.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/inadequatetrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://indonovels.blogspot.co.id/" target="_blank">https://indonovels.blogspot.co.id/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/indonovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://indowebnovel.id/" target="_blank">https://indowebnovel.id/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/indowebnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://infinitenoveltranslations.net/" target="_blank">https://infinitenoveltranslations.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/infinitetrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://instadoses.com/" target="_blank">https://instadoses.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/instadoses.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://isotls.com/" target="_blank">https://isotls.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/isotls.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://jpmtl.com/" target="_blank">https://jpmtl.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/jpmtl.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://jstranslations1.com/" target="_blank">https://jstranslations1.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/jstrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://justatranslatortranslations.com/" target="_blank">https://justatranslatortranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/justatrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://kiss-novel.com/" target="_blank">https://kiss-novel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/kissnovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://kisslightnovels.info/" target="_blank">https://kisslightnovels.info/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/kisslightnovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://lazybirdtranslations.wordpress.com/" target="_blank">https://lazybirdtranslations.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/ladybirdtrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://lemontreetranslations.wordpress.com/" target="_blank">https://lemontreetranslations.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lemontree.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://light-novel.online/" target="_blank">https://light-novel.online/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelonline.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://lightnovel.tv/" target="_blank">https://lightnovel.tv/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnoveltv.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://lightnovel.world/" target="_blank">https://lightnovel.world/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelworld.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://lightnovelbastion.com/" target="_blank">https://lightnovelbastion.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelbastion.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://lightnovelheaven.com/" target="_blank">https://lightnovelheaven.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelheaven.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://lightnovelkiss.com/" target="_blank">https://lightnovelkiss.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelkiss.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://lightnovelshub.com/" target="_blank">https://lightnovelshub.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelshub.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://lightnovelsonl.com/" target="_blank">https://lightnovelsonl.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelsonl.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://lightnovelstranslations.com/" target="_blank">https://lightnovelstranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovetrans.py">1627614560</a></td>
<td><span class="font-size: 0.8em">Marc-Andre Julien, SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://listnovel.com/" target="_blank">https://listnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/listnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://litnet.com/" target="_blank">https://litnet.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/booknet.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://ln.hako.re/" target="_blank">https://ln.hako.re/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lnhakone.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login">🔑</span></td>
<td><a href="https://lnmtl.com/" target="_blank">https://lnmtl.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lnmtl.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://m.1ksy.com/" target="_blank">https://m.1ksy.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/1ksy.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://m.chinesefantasynovels.com/" target="_blank">https://m.chinesefantasynovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/chinesefantasy.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, amritoo</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://m.mywuxiaworld.com/" target="_blank">https://m.mywuxiaworld.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mywuxiaworld.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, amritoo, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://m.readlightnovel.cc/" target="_blank">https://m.readlightnovel.cc/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readlightnovelcc.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://m.romanticlovebooks.com/" target="_blank">https://m.romanticlovebooks.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/romanticlb.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://m.webnovel.com/" target="_blank">https://m.webnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/webnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://m.wuxiaworld.co/" target="_blank">https://m.wuxiaworld.co/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaco.py">1627423436</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://mangatoon.mobi/" target="_blank">https://mangatoon.mobi/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mangatoon.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://meionovel.id/" target="_blank">https://meionovel.id/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/meionovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://miraslation.net/" target="_blank">https://miraslation.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/miraslation.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://moonstonetranslation.com/" target="_blank">https://moonstonetranslation.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/moonstonetrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://morenovel.net/" target="_blank">https://morenovel.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/morenovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://my.w.tt/" target="_blank">https://my.w.tt/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wattpad.py">1627776908</a></td>
<td><span class="font-size: 0.8em">Carter S, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://mysticalmerries.com/" target="_blank">https://mysticalmerries.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mysticalmerries.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://newsite.kolnovel.com/" target="_blank">https://newsite.kolnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/kolnovelnewsite.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novel27.com/" target="_blank">https://novel27.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novel27.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelcake.com/" target="_blank">https://novelcake.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelcake.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://novelextra.com/" target="_blank">https://novelextra.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelextra.py">1627556402</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelfull.com/" target="_blank">https://novelfull.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelfull.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelfullplus.com/" target="_blank">https://novelfullplus.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelfullplus.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelgate.net/" target="_blank">https://novelgate.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelgate.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://novelgo.id/" target="_blank">https://novelgo.id/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelgo.py">1627422652</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, fadhilm293</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://novelmic.com/" target="_blank">https://novelmic.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelmic.py">1627433129</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelonlinefree.com/" target="_blank">https://novelonlinefree.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelonlinefree.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelonlinefull.com/" target="_blank">https://novelonlinefull.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelonlinefull.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://novelringan.com/" target="_blank">https://novelringan.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelringan.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novels.pl/" target="_blank">https://novels.pl/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelspl.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelsite.net/" target="_blank">https://novelsite.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelsite.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://novelsonline.net/" target="_blank">https://novelsonline.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelsonline.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://novelsrock.com/" target="_blank">https://novelsrock.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelsrock.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://noveltoon.mobi/" target="_blank">https://noveltoon.mobi/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/noveltoon.py">1627271674</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://noveltranslate.com/" target="_blank">https://noveltranslate.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/noveltranslate.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://noveltrench.com/" target="_blank">https://noveltrench.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/noveltrench.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://omgnovels.com/" target="_blank">https://omgnovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/omgnovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://overabook.com/" target="_blank">https://overabook.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/overabook.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://ranobelib.me/" target="_blank">https://ranobelib.me/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/ranobelibme.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, juh9870</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://ranobes.net/" target="_blank">https://ranobes.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/ranobes.py">1627556362</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://readlightnovels.net/" target="_blank">https://readlightnovels.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readlightnovelsnet.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sakari Saastamoinen, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://readnovelfull.com/" target="_blank">https://readnovelfull.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readnovelfull.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://readnovelz.net/" target="_blank">https://readnovelz.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readnovelz.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://readwebnovels.net/" target="_blank">https://readwebnovels.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readwebnovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://reincarnationpalace.com/" target="_blank">https://reincarnationpalace.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/reincarnationpalace.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://rewayat.club/" target="_blank">https://rewayat.club/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/rewayatclub.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://rpgnoob.wordpress.com/" target="_blank">https://rpgnoob.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/rpgnovels.py">1627433129</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://rpgnovels.com/" target="_blank">https://rpgnovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/rpgnovels.py">1627433129</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://shalvationtranslations.wordpress.com/" target="_blank">https://shalvationtranslations.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/shalvation.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://skynovel.org/" target="_blank">https://skynovel.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/skynovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://sleepytranslations.com/" target="_blank">https://sleepytranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/sleepytrans.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://smnovels.com/" target="_blank">https://smnovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/smnovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://steambunlightnovel.com/" target="_blank">https://steambunlightnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/steambun.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://supernovel.net/" target="_blank">https://supernovel.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/supernovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://tiknovel.com/" target="_blank">https://tiknovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/tiknovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://toc.qidianunderground.org/" target="_blank">https://toc.qidianunderground.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/qidianunderground.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://tomotranslations.com/" target="_blank">https://tomotranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/tomotrans.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://totallytranslations.com/" target="_blank">https://totallytranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/totallytranslations.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://tunovelaligera.com/" target="_blank">https://tunovelaligera.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/tunovelaligera.py">1627556402</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://viewnovel.net/" target="_blank">https://viewnovel.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/viewnovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://vipnovel.com/" target="_blank">https://vipnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/vipnovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://vistranslations.wordpress.com/" target="_blank">https://vistranslations.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/vistrans.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wbnovel.com/" target="_blank">https://wbnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wbnovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://webnovel.online/" target="_blank">https://webnovel.online/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/webnovelonline.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://webnovelindonesia.com/" target="_blank">https://webnovelindonesia.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/webnovelindonesia.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://webnovelonline.com/" target="_blank">https://webnovelonline.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/webnovelonlinecom.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://wnmtl.org/" target="_blank">https://wnmtl.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wnmtl.py">1627909242</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wondernovels.com/" target="_blank">https://wondernovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wondernovels.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://woopread.com/" target="_blank">https://woopread.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/woopread.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Aakash Gajjar, SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wordexcerpt.com/" target="_blank">https://wordexcerpt.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wordexcerpt.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wordexcerpt.org/" target="_blank">https://wordexcerpt.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wordexcerpt.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://writerupdates.com/" target="_blank">https://writerupdates.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/writerupdates.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://wujizun.com/" target="_blank">https://wujizun.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wujizun.py">1627433129</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wuxiaworld.io/" target="_blank">https://wuxiaworld.io/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaworldio.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wuxiaworld.live/" target="_blank">https://wuxiaworld.live/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaworldlive.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://wuxiaworld.name/" target="_blank">https://wuxiaworld.name/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaworldio.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://wuxiaworld.online/" target="_blank">https://wuxiaworld.online/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaonline.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://wuxiaworld.site/" target="_blank">https://wuxiaworld.site/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiasite.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://wuxiaworldsite.co/" target="_blank">https://wuxiaworldsite.co/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaworldsite.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.1ksy.com/" target="_blank">https://www.1ksy.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/1ksy.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.aixdzs.com/" target="_blank">https://www.aixdzs.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/aixdzs.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.allnovel.org/" target="_blank">https://www.allnovel.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/allnovel.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.anonanemone.wordpress.com/" target="_blank">https://www.anonanemone.wordpress.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/anonanemone.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.asianhobbyist.com/" target="_blank">https://www.asianhobbyist.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/asianhobbyist.py">1628465042</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.box-novel.com/" target="_blank">https://www.box-novel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/boxnovelcom.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.daocaorenshuwu.com/" target="_blank">https://www.daocaorenshuwu.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/daocaorenshuwu.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.f-w-o.com/" target="_blank">https://www.f-w-o.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fantasyworldonline.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.fanfiction.net/" target="_blank">https://www.fanfiction.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fanfiction.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, fof300f</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.flying-lines.com/" target="_blank">https://www.flying-lines.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/flyinglines.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.foxaholic.com/" target="_blank">https://www.foxaholic.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/foxaholic.py">1627433129</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.foxteller.com/" target="_blank">https://www.foxteller.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/foxteller.py">1627433129</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.freelightnovel.com/" target="_blank">https://www.freelightnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/freelightnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.fuyuneko.org/" target="_blank">https://www.fuyuneko.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/fuyuneko.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, SirGryphin, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.idqidian.us/" target="_blank">https://www.idqidian.us/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/idqidian.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.koreanmtl.online/" target="_blank">https://www.koreanmtl.online/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/koreanmtl.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.lightnovelpub.com/" target="_blank">https://www.lightnovelpub.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelpub.py">1628406176</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.lightnovelworld.com/" target="_blank">https://www.lightnovelworld.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lightnovelpub.py">1628406176</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.lunarletters.com/" target="_blank">https://www.lunarletters.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/lunarletters.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.machine-translation.org/" target="_blank">https://www.machine-translation.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/machinetransorg.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.miraslation.net/" target="_blank">https://www.miraslation.net/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/miraslation.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.mtlreader.com/" target="_blank">https://www.mtlreader.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mtlreader.py">1627918903</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.mywuxiaworld.com/" target="_blank">https://www.mywuxiaworld.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/mywuxiaworld.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, amritoo, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.novelall.com/" target="_blank">https://www.novelall.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelall.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.novelcool.com/" target="_blank">https://www.novelcool.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelcool.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.novelhall.com/" target="_blank">https://www.novelhall.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelhall.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.novelhunters.com/" target="_blank">https://www.novelhunters.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelhunters.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.novelmultiverse.com/" target="_blank">https://www.novelmultiverse.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelmultiverse.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.novelpassion.com/" target="_blank">https://www.novelpassion.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelpassion.py">1627268414</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.novels.pl/" target="_blank">https://www.novels.pl/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelspl.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.novelupdates.cc/" target="_blank">https://www.novelupdates.cc/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/novelupdatescc.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.oppatranslations.com/" target="_blank">https://www.oppatranslations.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/oppatrans.py">1626444718</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.ornovel.com/" target="_blank">https://www.ornovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/ornovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.readlightnovel.cc/" target="_blank">https://www.readlightnovel.cc/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readlightnovelcc.py">1627423436</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.readlightnovel.org/" target="_blank">https://www.readlightnovel.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readln.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.readwn.com/" target="_blank">https://www.readwn.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/readwn.py">1627279152</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.romanticlovebooks.com/" target="_blank">https://www.romanticlovebooks.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/romanticlb.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.royalroad.com/" target="_blank">https://www.royalroad.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/royalroad.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Pk11, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.scribblehub.com/" target="_blank">https://www.scribblehub.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/scribblehub.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Pk11, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.shinsori.com/" target="_blank">https://www.shinsori.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/shinsori.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.tapread.com/" target="_blank">https://www.tapread.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/tapread.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.tiknovel.com/" target="_blank">https://www.tiknovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/9kqw.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Galunid, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.virlyce.com/" target="_blank">https://www.virlyce.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/virlyce.py">1627268414</a></td>
<td><span class="font-size: 0.8em">AncientCatz, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.volarenovels.com/" target="_blank">https://www.volarenovels.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/volarenovels.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.wattpad.com/" target="_blank">https://www.wattpad.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wattpad.py">1627776908</a></td>
<td><span class="font-size: 0.8em">Carter S, Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.webnovel.com/" target="_blank">https://www.webnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/webnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.webnovelover.com/" target="_blank">https://www.webnovelover.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/webnovelover.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.wnmtl.org/" target="_blank">https://www.wnmtl.org/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wnmtl.py">1627909242</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.worldnovel.online/" target="_blank">https://www.worldnovel.online/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/worldnovelonline.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.wuxialeague.com/" target="_blank">https://www.wuxialeague.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxialeague.py">1626444718</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.wuxiaworld.co/" target="_blank">https://www.wuxiaworld.co/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiaco.py">1627423436</a></td>
<td><span class="font-size: 0.8em">Galunid, SirGryphin, Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://www.wuxiaworld.com/" target="_blank">https://www.wuxiaworld.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/wuxiacom.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Sudipto Chandra Dipu, Yudi Santoso, dipu-bd, kuwoyuki</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.x81zw.com/" target="_blank">https://www.x81zw.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/x81zw.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.xiainovel.com/" target="_blank">https://www.xiainovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/xiainovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://www.xsbiquge.com/" target="_blank">https://www.xsbiquge.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/xsbiquge.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching"></span><span title="Supports Login"></span></td>
<td><a href="https://yukinovel.id/" target="_blank">https://yukinovel.id/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/yukinovel.py">1627268414</a></td>
<td><span class="font-size: 0.8em">Sudipto Chandra, Yudi Santoso, dipu-bd</span></td>
</tr>
<tr><td class="cursor: default"><span title="Supports Searching">🔍</span><span title="Supports Login"></span></td>
<td><a href="https://zinnovel.com/" target="_blank">https://zinnovel.com/</a></td>
<td><a href="https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/zinnovel.py">1626444718</a></td>
<td><span class="font-size: 0.8em">SirGryphin, Sudipto Chandra</span></td>
</tr>
</tbody>
</table>

<!-- auto generated supported sources list -->

## Rejected sources

<!-- auto generated rejected sources list -->

<table>
<tbody>
<tr><th>Source URL</th>
<th>Rejection Cause</th>
</tr>
<tr><td><a href="http://fullnovel.live/" target="_blank">http://fullnovel.live/</a></td>
<td>This site can’t be reached</td>
</tr>
<tr><td><a href="http://gravitytales.com/" target="_blank">http://gravitytales.com/</a></td>
<td>Domain is expired</td>
</tr>
<tr><td><a href="https://4scanlation.com/" target="_blank">https://4scanlation.com/</a></td>
<td>Domain expired</td>
</tr>
<tr><td><a href="https://anythingnovel.com/" target="_blank">https://anythingnovel.com/</a></td>
<td>Site broken</td>
</tr>
<tr><td><a href="https://bestoflightnovels.com/" target="_blank">https://bestoflightnovels.com/</a></td>
<td>Site moved</td>
</tr>
<tr><td><a href="https://chrysanthemumgarden.com/" target="_blank">https://chrysanthemumgarden.com/</a></td>
<td>Removed on request of the owner (Issue #649)</td>
</tr>
<tr><td><a href="https://dsrealmtranslations.com/" target="_blank">https://dsrealmtranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://fsapk.com/" target="_blank">https://fsapk.com/</a></td>
<td>Site is not working</td>
</tr>
<tr><td><a href="https://indomtl.com/" target="_blank">https://indomtl.com/</a></td>
<td>Does not like to be crawled</td>
</tr>
<tr><td><a href="https://mtled-novels.com/" target="_blank">https://mtled-novels.com/</a></td>
<td>Domain is expired</td>
</tr>
<tr><td><a href="https://myoniyonitranslations.com/" target="_blank">https://myoniyonitranslations.com/</a></td>
<td>522 - Connection timed out</td>
</tr>
<tr><td><a href="https://novelcrush.com/" target="_blank">https://novelcrush.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelplanet.com/" target="_blank">https://novelplanet.com/</a></td>
<td>Site is closed</td>
</tr>
<tr><td><a href="https://novelraw.blogspot.com/" target="_blank">https://novelraw.blogspot.com/</a></td>
<td>Site closed down</td>
</tr>
<tr><td><a href="https://pery.info/" target="_blank">https://pery.info/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.centinni.com/" target="_blank">https://www.centinni.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelspread.com/" target="_blank">https://www.novelspread.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.noveluniverse.com/" target="_blank">https://www.noveluniverse.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelv.com/" target="_blank">https://www.novelv.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.rebirth.online/" target="_blank">https://www.rebirth.online/</a></td>
<td>Site moved</td>
</tr>
<tr><td><a href="https://www.translateindo.com/" target="_blank">https://www.translateindo.com/</a></td>
<td>Site is down</td>
</tr>
</tbody>
</table>

<!-- auto generated rejected sources list -->

## Supported output formats

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
