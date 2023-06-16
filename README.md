# Lightnovel Crawler

[![download win](https://img.shields.io/badge/download-lncrawl.exe-red?logo=windows&style=for-the-badge)](https://rebrand.ly/lncrawl)
[![download linux](<https://img.shields.io/badge/download-lncrawl_(linux)-brown?logo=linux&style=for-the-badge>)](https://rebrand.ly/lncrawl-linux)
[![Discord](https://img.shields.io/discord/578550900231110656?logo=discord&label=discord&style=for-the-badge)](https://discord.gg/wMECG2Q)
<br>
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg?logo=python)](https://pypi.org/project/lightnovel-crawler)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
[![Build and Publish](https://github.com/dipu-bd/lightnovel-crawler/actions/workflows/release.yml/badge.svg)](https://github.com/dipu-bd/lightnovel-crawler/actions/workflows/release.yml)

<!-- [![GitHub stars](https://img.shields.io/github/stars/dipu-bd/lightnovel-crawler?logo=github)](https://github.com/dipu-bd/lightnovel-crawler) -->
<!-- [![AppVeyor](https://img.shields.io/appveyor/build/dipu-bd/lightnovel-crawler?logo=appveyor)](https://ci.appveyor.com/project/dipu-bd/lightnovel-crawler) -->
<!-- [![travis-ci](https://travis-ci.com/dipu-bd/lightnovel-crawler.svg?branch=master)](https://travis-ci.com/dipu-bd/lightnovel-crawler) -->

An app to download novels from online sources and generate e-books.

> **Discord: [https://discord.gg/wMECG2Q](https://discord.gg/wMECG2Q)**

> **Telegram: [https://t.me/epub_smelter_bot](https://t.me/epub_smelter_bot)**

## Table of contents

- [Lightnovel Crawler](#lightnovel-crawler)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
    - [Standalone Bundle (Windows, Linux)](#standalone-bundle-windows-linux)
    - [PIP (Windows, Mac, and Linux)](#pip-windows-mac-and-linux)
    - [PIP (Directly from GitHub)](#pip-directly-from-github)
    - [Docker](#docker)
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
    - [Additional Help](#additional-help)
    - [Login to **www.wuxiaworld.com**](#login-to-wwwwuxiaworldcom)
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

<!-- brew install python-tk -->

### Standalone Bundle (Windows, Linux)

⏬ **Windows**: [lncrawl.exe ~ 25MB](https://rebrand.ly/lncrawl)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program.

⏬ **Linux**: [lncrawl ~ 30MB](https://rebrand.ly/lncrawl-linux)

> It is recommended to install via **pip** if you are on Linux

⏬ _To get older versions visit the [Releases page](https://github.com/dipu-bd/lightnovel-crawler/releases)_

### PIP (Windows, Mac, and Linux)

📦 A python package named `lightnovel-crawler` is available at [pypi](https://pypi.org/project/lightnovel-crawler).

> Make sure you have installed **Python** v3.7 or higher and have **pip** enabled. Visit these links to install python with pip in [Windows](https://stackoverflow.com/a/44437176/1583052), [Linux](https://stackoverflow.com/a/51799221/1583052) and [MacOS](https://itsevans.com/install-pip-osx/). Feel free to ask on the Discord server if you are stuck.

To install this app or to update installed one via `pip`, just run:

```bash
$ pip install -U lightnovel-crawler
```

In some cases you have to use `python3 -m pip` or `pip3` or `python -m pip`. And you do not need `--user` option, if you are running from root.

Next, open your terminal and enter:

```
$ lncrawl
```

> To view extra logs, use: `lncrawl -lll`

If you want to get the cutting-edge (sometimes unstable) from the `dev` branch, you can get it by:

### PIP (Directly from GitHub)

The `master` branch contains the latest stable code. If you can not wait for it to be released in the PyPi, you can get it like this:

```
$ pip install -U git+https://github.com/dipu-bd/lightnovel-crawler.git#egg=lightnovel-crawler
```

The `dev` branch contains cutting-edge, sometimes unstable changes. To install it:

```
$ pip install -U https://github.com/dipu-bd/lightnovel-crawler/tarball/refs/heads/dev#egg=lightnovel-crawler
```

### Docker

Docker is a convenient way to run it anywhere.

- First clone the project.

```
$ git clone https://github.com/dipu-bd/lightnovel-crawler
```

- Build docker:

```
$ cd lightnovel-crawler
$ docker build -t lncrawl -f ./scripts/Dockerfile .
```

- Run commands using docker:

```
$ mkdir ~/Lightnovels
$ docker run -v ~/Lightnovels:/home/appuser/app/Lightnovels -it lncrawl
```

> You can setup _alias_ to the above command in your terminal's profile to run using single a single-word command.

### Termux (Android)

> Please read before proceeding:
>
> - It is not guaranteed that the app will run smoothly in all devices.
> - It may take a long time to install depending on your mobile processor.
> - It is recommended to use the bots on either Discord or Telegram if you are on mobile.

📱 Using Termux, you can run this app in your android phones too. Follow this instructions:

- Install [Termux](https://play.google.com/store/apps/details?id=com.termux) from playstore.
- Open the app and run these commands one by one:
  - `pkg upgrade`
  - `pkg install python libxml2 libxslt libjpeg-turbo webp rust`
  - `pip install -U pip wheel setuptools`
  - `pip install lightnovel-crawler`
  - `termux-setup-storage`
  - `cd ~/storage/downloads`
  - `lncrawl`
- You can navigate up using <kbd>Vol UP</kbd> + <kbd>W</kbd> and down using <kbd>Vol UP</kbd> + <kbd>S</kbd>.

When there is a new update available, you can install it just by running `pip install -U lightnovel-crawler`. You will not have to run all the above commands again.

**PyDroid**

You can also use PyDroid in Android phones. Check this discussion for a custom script to run the app: https://github.com/dipu-bd/lightnovel-crawler/discussions/1137

<!-- TODO -->
<!-- ### Google Colab -->

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
$ pip install -r requirements.txt
```

- Run the program (use python v3.7 or higher):

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
$ pip3 install -r requirements.txt
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

<!-- auto generated command line output -->
```bash
$ lncrawl -h
================================================================================
╭╮╱╱╱╱╱╱╭╮╱╭╮╱╱╱╱╱╱╱╱╱╱╱╱╭╮╱╭━━━╮╱╱╱╱╱╱╱╱╱╭╮
┃┃╱╱╱╱╱╱┃┃╭╯╰╮╱╱╱╱╱╱╱╱╱╱╱┃┃╱┃╭━╮┃╱╱╱╱╱╱╱╱╱┃┃
┃┃╱╱╭┳━━┫╰┻╮╭╋━╮╭━━┳╮╭┳━━┫┃╱┃┃╱╰╋━┳━━┳╮╭╮╭┫┃╭━━┳━╮
┃┃╱╭╋┫╭╮┃╭╮┃┃┃╭╮┫╭╮┃╰╯┃┃━┫┃╱┃┃╱╭┫╭┫╭╮┃╰╯╰╯┃┃┃┃━┫╭╯
┃╰━╯┃┃╰╯┃┃┃┃╰┫┃┃┃╰╯┣╮╭┫┃━┫╰╮┃╰━╯┃┃┃╭╮┣╮╭╮╭┫╰┫┃━┫┃
╰━━━┻┻━╮┣╯╰┻━┻╯╰┻━━╯╰╯╰━━┻━╯╰━━━┻╯╰╯╰╯╰╯╰╯╰━┻━━┻╯
╱╱╱╱╱╭━╯┃ v3.2.6
╱╱╱╱╱╰━━╯ 🔗 https://github.com/dipu-bd/lightnovel-crawler
--------------------------------------------------------------------------------
usage: lncrawl [options...]
       lightnovel-crawler [options...]

options:
  -h, --help            show this help message and exit

  -v, --version         show program's version number and exit
  -l                    Set log levels. (-l = warn, -ll = info, -lll = debug).
  --log-file [FILE]     To store application logs to a file.
  --list-sources        Display a list of available sources.
  --crawler [FILES ...]
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
  --page START [STOP. ...]
                        The start and final chapter urls.
  --range FROM TO., --index FROM TO., --chapter FROM TO.
                        The start and final chapter indexes.
  --volumes [N ...]     The list of volume numbers to download.
  --chapters [URL ...]  A list of specific chapter urls.
  --proxy-file FILE     Proxies as SCHEME://HOST:PORT@USER:PASSWORD format in
                        each line. All except HOST are optional
  --auto-proxy          Use some free proxies from https://free-proxy-
                        list.net/
  --bot {console,telegram,discord,lookup}
                        Select a bot. Default: console.
  --shard-id [SHARD_ID]
                        Discord bot shard id (default: 0)
  --shard-count [SHARD_COUNT]
                        Discord bot shard counts (default: 1)
  --selenium-grid URL   Selenium Grid URL for Chrome Webdriver
  --suppress            Suppress all input prompts and use defaults.
  --close-directly      Do not prompt to close at the end for windows
                        platforms.
  --resume [NAME/URL]   Resume download of a novel containing in
                        /home/runner/work/lightnovel-crawler/lightnovel-
                        crawler/Lightnovels
  ENV                   [chatbots only] Pass query string at the end of all
                        options. It will be use instead of .env file. Sample:
                        "BOT=discord&DISCORD_TOKEN=***&LOG_LEVEL=DEBUG"

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~

--------------------------------------------------------------------------------
 🔗  https://github.com/dipu-bd/lightnovel-crawler/issues 
================================================================================
```
<!-- auto generated command line output -->

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

### Additional Help

Visit the [discussions](https://github.com/dipu-bd/lightnovel-crawler/discussions) page for more information. You can also post your query there too.

### Login to [www.wuxiaworld.com](https://www.wuxiaworld.com/)

Follow this guide to know how to login: https://github.com/dipu-bd/lightnovel-crawler/discussions/1360

## Development

You are very welcome to contribute in this project. You can:

- create new issues pointing out the bugs.
- solve existing issues.
- add your own sources.
- add new output formats.
- create new bots.

### Adding new source

- Use `lncrawl --bot lookup` first to auto-generate your crawler from an existing template.
- Check inside the [`sources/_examples`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/_examples). Read all the comments of all the files. And pick the one you like.
- You can find plenty examples in the `sources` folder. Try to check the latest ones
- Put your source file inside the language folder.
  The `en` folder has too many files, therefore it is grouped using the first letter of the domain name.
- Before making commit format files using `blake` formatter, and use `scripts/lint.sh` or `scripts/lint.bat` to check linting issues.

### Adding new Bot

- Create a new bot file using [`bots/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/_sample.py) as template.
- Import bot to [`bots/__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/__init__.py) file.

## Supported sources

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose).

<!-- auto generated supported sources list -->

We are supporting 334 sources and 320 crawlers.

### `~` Unknown

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://es.mtlnovel.com/" target="_blank">http://es.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://fr.mtlnovel.com/" target="_blank">http://fr.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://id.mtlnovel.com/" target="_blank">http://id.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.mtlnovel.com/" target="_blank">http://www.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://18.foxaholic.com/" target="_blank">https://18.foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/foxaholic.py" title="03 October 2022 11:27:34 PM">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://es.mtlnovel.com/" target="_blank">https://es.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://foxaholic.com/" target="_blank">https://foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/foxaholic.py" title="03 October 2022 11:27:34 PM">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fr.mtlnovel.com/" target="_blank">https://fr.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://global.foxaholic.com/" target="_blank">https://global.foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/foxaholic.py" title="03 October 2022 11:27:34 PM">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://id.mtlnovel.com/" target="_blank">https://id.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://my.w.tt/" target="_blank">https://my.w.tt/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/wattpad.py" title="07 January 2023 07:27:43 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ncode.syosetu.com/" target="_blank">https://ncode.syosetu.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/jp/s/syosetu.py" title="19 January 2023 06:18:06 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.foxaholic.com/" target="_blank">https://www.foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/foxaholic.py" title="03 October 2022 11:27:34 PM">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlnovel.com/" target="_blank">https://www.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/mtlnovel.py" title="02 October 2022 08:48:50 PM">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelupdates.com/" target="_blank">https://www.novelupdates.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/novelupdates.py" title="07 December 2022 01:21:00 PM">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.quotev.com/" target="_blank">https://www.quotev.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/quotev.py" title="29 September 2022 11:43:13 AM">4</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wattpad.com/" target="_blank">https://www.wattpad.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/multi/wattpad.py" title="07 January 2023 07:27:43 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
</tbody>
</table>


### `ar` Arabic

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://arnovel.me/" target="_blank">https://arnovel.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/ar/arnovel.py" title="02 February 2023 03:53:13 PM">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://kolnovel.com/" target="_blank">https://kolnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/ar/kolnovel.py" title="23 February 2023 12:26:02 AM">1</a></td>
<td></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rewayat.club/" target="_blank">https://rewayat.club/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/ar/rewayatclub.py" title="27 September 2022 08:36:43 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `en` English

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://novelfull.com/" target="_blank">http://novelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelfull.py" title="04 October 2022 08:04:38 PM">49</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://ranobes.net/" target="_blank">http://ranobes.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/ranobes.py" title="03 October 2022 11:27:34 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://readonlinenovels.com/" target="_blank">http://readonlinenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readonlinenovels.py" title="04 November 2022 02:46:53 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/amritoo"><img src="https://avatars.githubusercontent.com/u/45586379?v=4&s=24" alt="amritoo" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://wnmtl.org/" target="_blank">http://wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wnmtl.py" title="02 October 2022 08:48:50 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.fujitranslation.com/" target="_blank">http://www.fujitranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fujitrans.py" title="27 September 2022 07:22:47 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.wnmtl.org/" target="_blank">http://www.wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wnmtl.py" title="02 October 2022 08:48:50 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zenithnovels.com/" target="_blank">http://zenithnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/z/zenithnovels.py" title="09 December 2022 01:10:58 AM">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://1stkissnovel.love/" target="_blank">https://1stkissnovel.love/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/1/1stkissnovel.py" title="16 June 2023 03:34:48 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://1stkissnovel.org/" target="_blank">https://1stkissnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/1/1stkissnovel.py" title="16 June 2023 03:34:48 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://88tangeatdrinkread.wordpress.com/" target="_blank">https://88tangeatdrinkread.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/8/88tang.py" title="27 September 2022 07:22:47 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://allnovel.org/" target="_blank">https://allnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/allnovel.py" title="04 October 2022 08:04:38 PM">47</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://allnovelfull.com/" target="_blank">https://allnovelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/allnovelfull.py" title="04 October 2022 04:56:59 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://americanfaux.com/" target="_blank">https://americanfaux.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/americanfaux.py" title="27 September 2022 07:22:47 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://amnesiactl.com/" target="_blank">https://amnesiactl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/amnesiactl.py" title="27 September 2022 08:36:43 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ancientheartloss.com/" target="_blank">https://ancientheartloss.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/ancientheartloss.py" title="27 September 2022 07:22:47 PM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ancientheartloss.wordpress.com/" target="_blank">https://ancientheartloss.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/ancientheartloss.py" title="27 September 2022 07:22:47 PM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://api.babelnovel.com/" target="_blank">https://api.babelnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/babelnovel.py" title="20 September 2022 08:44:28 AM">30</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://aquamanga.com/" target="_blank">https://aquamanga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/aquamanga.py" title="27 September 2022 08:34:44 PM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://asadatranslations.com/" target="_blank">https://asadatranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/asadatrans.py" title="27 September 2022 08:34:44 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://automtl.wordpress.com/" target="_blank">https://automtl.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/automtl.py" title="02 October 2022 08:48:50 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://babelnovel.com/" target="_blank">https://babelnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/babelnovel.py" title="20 September 2022 08:44:28 AM">30</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bakapervert.wordpress.com/" target="_blank">https://bakapervert.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bakapervert.py" title="27 September 2022 07:22:47 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://bato.to/" target="_blank">https://bato.to/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://batocc.com/" target="_blank">https://batocc.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://batotoo.com/" target="_blank">https://batotoo.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://batotwo.com/" target="_blank">https://batotwo.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://battwo.com/" target="_blank">https://battwo.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://beautymanga.com/" target="_blank">https://beautymanga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/beautymanga.py" title="06 April 2023 10:22:58 AM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bestlightnovel.com/" target="_blank">https://bestlightnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bestlightnovel.py" title="20 April 2023 03:20:01 AM">25</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bonnovel.com/" target="_blank">https://bonnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bonnovel.py" title="18 January 2023 10:05:15 PM">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://booknet.com/" target="_blank">https://booknet.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/booknet.py" title="03 October 2022 11:27:34 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://boxnovel.com/" target="_blank">https://boxnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/boxnovel.py" title="16 November 2022 11:38:03 AM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bronovel.com/" target="_blank">https://bronovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bronovel.py" title="27 September 2022 07:22:47 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://chapmanganato.com/" target="_blank">https://chapmanganato.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readmanganato.py" title="14 December 2022 04:17:52 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://chrysanthemumgarden.com/" target="_blank">https://chrysanthemumgarden.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/c/chrysanthemumgarden.py" title="27 September 2022 07:46:30 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://coffeemanga.com/" target="_blank">https://coffeemanga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/c/coffeemanga.py" title="27 September 2022 07:22:47 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://comiko.net/" target="_blank">https://comiko.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://comrademao.com/" target="_blank">https://comrademao.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/c/fu_kemao.py" title="02 October 2022 08:48:50 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://creativenovels.com/" target="_blank">https://creativenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/c/creativenovels.py" title="09 December 2022 01:10:58 AM">32</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://crescentmoon.blog/" target="_blank">https://crescentmoon.blog/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/c/crescentmoon.py" title="27 September 2022 07:22:47 PM">58</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://daonovel.com/" target="_blank">https://daonovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/daonovel.py" title="17 January 2023 01:49:04 AM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://demontranslations.com/" target="_blank">https://demontranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/demontrans.py" title="27 September 2022 08:36:43 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dmtranslationscn.com/" target="_blank">https://dmtranslationscn.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/dmtrans.py" title="27 September 2022 07:22:47 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dobelyuwai.wordpress.com/" target="_blank">https://dobelyuwai.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/dobelyuwai.py" title="02 October 2022 08:48:50 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dragontea.ink/" target="_blank">https://dragontea.ink/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/dragon_tea.py" title="27 September 2022 08:36:43 PM">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://dto.to/" target="_blank">https://dto.to/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dummynovels.com/" target="_blank">https://dummynovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/dummynovels.py" title="27 September 2022 08:34:44 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://exiledrebelsscanlations.com/" target="_blank">https://exiledrebelsscanlations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/e/exiledrebels.py" title="27 September 2022 07:22:47 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://f-w-o.com/" target="_blank">https://f-w-o.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fantasyworldonline.py" title="27 September 2022 07:22:47 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fanstranslations.com/" target="_blank">https://fanstranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fanstrans.py" title="27 September 2022 08:34:44 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://freefullnovel.com/" target="_blank">https://freefullnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/freefullnovel.py" title="02 October 2022 08:48:50 PM">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://freemanga.me/" target="_blank">https://freemanga.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/freemanga.py" title="27 September 2022 08:34:44 PM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://freewebnovel.com/" target="_blank">https://freewebnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/freewebnovel.py" title="02 February 2023 03:45:45 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fujitranslation.com/" target="_blank">https://fujitranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fujitrans.py" title="27 September 2022 07:22:47 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://harimanga.com/" target="_blank">https://harimanga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/h/harimanga.py" title="27 September 2022 08:34:44 PM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hostednovel.com/" target="_blank">https://hostednovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/h/hostednovel.py" title="27 September 2022 08:36:43 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hotnovelfull.com/" target="_blank">https://hotnovelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/h/hotnovelfull.py" title="07 October 2022 05:03:19 PM">77</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://hto.to/" target="_blank">https://hto.to/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hui3r.wordpress.com/" target="_blank">https://hui3r.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/h/hui3r.py" title="27 September 2022 08:36:43 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://imperfectcomic.org/" target="_blank">https://imperfectcomic.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/imperfectcomic.py" title="10 October 2022 04:36:56 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://inadequatetranslations.wordpress.com/" target="_blank">https://inadequatetranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/inadequatetrans.py" title="27 September 2022 07:22:47 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://infinitenoveltranslations.net/" target="_blank">https://infinitenoveltranslations.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/infinitetrans.py" title="27 September 2022 07:22:47 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://isekaiscan.com/" target="_blank">https://isekaiscan.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/isekaiscan.py" title="17 January 2023 04:39:24 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://isekaiscan.eu/" target="_blank">https://isekaiscan.eu/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/isekaiscaneu.py" title="19 January 2023 06:28:58 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://isotls.com/" target="_blank">https://isotls.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/isotls.py" title="08 September 2022 05:57:51 PM">59</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jpmtl.com/" target="_blank">https://jpmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/j/jpmtl.py" title="02 October 2022 08:48:50 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://justatranslatortranslations.com/" target="_blank">https://justatranslatortranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/j/justatrans.py" title="27 September 2022 07:22:47 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://king-manga.com/" target="_blank">https://king-manga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/k/kingmanga.py" title="27 September 2022 08:34:44 PM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://kissmanga.in/" target="_blank">https://kissmanga.in/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/k/kissmanga.py" title="27 September 2022 08:34:44 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://latestnovel.net/" target="_blank">https://latestnovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/latestnovel.py" title="27 September 2022 07:46:30 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/BorgSquared"><img src="https://avatars.githubusercontent.com/u/7807834?v=4&s=24" alt="BorgSquared" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lazybirdtranslations.wordpress.com/" target="_blank">https://lazybirdtranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/ladybirdtrans.py" title="27 September 2022 07:22:47 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lazygirltranslations.com/" target="_blank">https://lazygirltranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lazygirltranslations.py" title="24 November 2022 12:22:05 AM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lemontreetranslations.wordpress.com/" target="_blank">https://lemontreetranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lemontree.py" title="27 September 2022 07:22:47 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://librarynovel.com/" target="_blank">https://librarynovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/librarynovel.py" title="27 September 2022 07:22:47 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovel.world/" target="_blank">https://lightnovel.world/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelworld.py" title="27 September 2022 08:36:43 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelbastion.com/" target="_blank">https://lightnovelbastion.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelbastion.py" title="03 October 2022 11:27:34 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelheaven.com/" target="_blank">https://lightnovelheaven.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelheaven.py" title="27 September 2022 07:22:47 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelreader.me/" target="_blank">https://lightnovelreader.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelreader.py" title="27 January 2023 08:37:27 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovels.me/" target="_blank">https://lightnovels.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelme.py" title="12 October 2022 11:17:53 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelsonl.com/" target="_blank">https://lightnovelsonl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelsonl.py" title="27 September 2022 07:46:30 PM">20</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelstranslations.com/" target="_blank">https://lightnovelstranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovetrans.py" title="12 September 2022 02:41:08 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://listnovel.com/" target="_blank">https://listnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/listnovel.py" title="27 September 2022 08:36:43 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lnmtl.com/" target="_blank">https://lnmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lnmtl.py" title="02 October 2022 08:48:50 PM">97</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lnreader.org/" target="_blank">https://lnreader.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelreader.py" title="27 January 2023 08:37:27 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lunarletters.com/" target="_blank">https://lunarletters.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lunarletters.py" title="27 September 2022 07:22:47 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.readlightnovel.cc/" target="_blank">https://m.readlightnovel.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readlightnovelcc.py" title="27 September 2022 08:36:43 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.webnovel.com/" target="_blank">https://m.webnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/webnovel.py" title="10 October 2022 09:54:59 AM">89</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.wuxiaworld.co/" target="_blank">https://m.wuxiaworld.co/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiaco.py" title="03 October 2022 11:27:34 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://manga-tx.com/" target="_blank">https://manga-tx.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/manga-tx.py" title="27 September 2022 08:34:44 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangabuddy.com/" target="_blank">https://mangabuddy.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangabuddy.py" title="23 November 2022 11:17:15 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangachill.io/" target="_blank">https://mangachill.io/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangachilllove.py" title="27 September 2022 07:22:47 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangachill.love/" target="_blank">https://mangachill.love/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangachilllove.py" title="27 September 2022 07:22:47 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangarockteam.com/" target="_blank">https://mangarockteam.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangarockteam.py" title="24 September 2022 01:47:47 AM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangarosie.love/" target="_blank">https://mangarosie.love/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangarosie.py" title="27 September 2022 08:34:44 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangarosie.me/" target="_blank">https://mangarosie.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangarosie.py" title="27 September 2022 08:34:44 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangastic.net/" target="_blank">https://mangastic.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangastic.py" title="30 January 2023 03:52:27 PM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mangatoon.mobi/" target="_blank">https://mangatoon.mobi/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangatoon.py" title="27 September 2022 08:36:43 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangatoto.com/" target="_blank">https://mangatoto.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangatoto.net/" target="_blank">https://mangatoto.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangatoto.org/" target="_blank">https://mangatoto.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangatx.com/" target="_blank">https://mangatx.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangatx.py" title="27 September 2022 08:34:44 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangaweebs.in/" target="_blank">https://mangaweebs.in/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangaweebs.py" title="27 September 2022 08:34:44 PM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://manhuaplus.online/" target="_blank">https://manhuaplus.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/manhuaplus.py" title="02 February 2023 03:53:13 PM">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://manhwachill.com/" target="_blank">https://manhwachill.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/manhwachill.py" title="27 September 2022 07:22:47 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://meownovel.com/" target="_blank">https://meownovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/meownovel.py" title="27 September 2022 08:34:44 PM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://miraslation.net/" target="_blank">https://miraslation.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/miraslation.py" title="21 September 2022 05:54:36 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mixednovel.net/" target="_blank">https://mixednovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mixednovel.py" title="18 January 2023 06:18:05 AM">5</a></td>
<td><a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/hoangphuc05"><img src="https://avatars.githubusercontent.com/u/15669865?v=4&s=24" alt="hoangphuc05" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mltnovels.com/" target="_blank">https://mltnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mltnovels.py" title="10 October 2022 03:39:48 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mostnovel.com/" target="_blank">https://mostnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mostnovel.py" title="27 September 2022 07:22:47 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mtlnation.com/" target="_blank">https://mtlnation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mtlnation.py" title="24 November 2022 12:39:06 AM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mtlreader.com/" target="_blank">https://mtlreader.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mtlreader.py" title="02 October 2022 08:48:50 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mto.to/" target="_blank">https://mto.to/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://myboxnovel.com/" target="_blank">https://myboxnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/myboxnovel.py" title="08 October 2022 07:45:40 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://myreadingmanga.fit/" target="_blank">https://myreadingmanga.fit/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/beautymanga.py" title="06 April 2023 10:22:58 AM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mysticalmerries.com/" target="_blank">https://mysticalmerries.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mysticalmerries.py" title="27 September 2022 08:36:43 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://newnovel.org/" target="_blank">https://newnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/newnovelorg.py" title="19 October 2022 08:32:28 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noblemtl.com/" target="_blank">https://noblemtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/noblemtl.py" title="10 October 2022 04:30:09 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://noobchan.xyz/" target="_blank">https://noobchan.xyz/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/noobchan.py" title="27 September 2022 08:34:44 PM">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novel27.com/" target="_blank">https://novel27.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novel27.py" title="27 September 2022 08:36:43 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novel35.com/" target="_blank">https://novel35.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novel35.py" title="30 September 2022 07:45:42 PM">1</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelbin.com/" target="_blank">https://novelbin.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelbin.py" title="04 October 2022 12:52:06 PM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelbin.net/" target="_blank">https://novelbin.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelbin.net.py" title="29 November 2022 03:01:01 PM">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelcake.com/" target="_blank">https://novelcake.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelcake.py" title="27 September 2022 08:36:43 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfull.com/" target="_blank">https://novelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelfull.py" title="04 October 2022 08:04:38 PM">49</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfull.me/" target="_blank">https://novelfull.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelfullme.py" title="01 November 2022 11:43:19 PM">2</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfullplus.com/" target="_blank">https://novelfullplus.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelfullplus.py" title="04 October 2022 08:04:38 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelgate.net/" target="_blank">https://novelgate.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelgate.py" title="27 September 2022 08:36:43 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelhard.com/" target="_blank">https://novelhard.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelhard.py" title="30 September 2022 02:34:32 AM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelhi.com/" target="_blank">https://novelhi.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelhi.py" title="19 January 2023 06:23:27 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelhulk.com/" target="_blank">https://novelhulk.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelhulk.py" title="04 October 2022 12:46:24 PM">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelmao.com/" target="_blank">https://novelmao.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelmao.py" title="02 October 2022 08:48:50 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://novelmic.com/" target="_blank">https://novelmic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelmic.py" title="27 September 2022 08:36:43 PM">20</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelnext.com/" target="_blank">https://novelnext.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelnext.py" title="12 October 2022 02:33:44 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelonlinefree.com/" target="_blank">https://novelonlinefree.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelonlinefree.py" title="27 September 2022 08:36:43 PM">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelonlinefull.com/" target="_blank">https://novelonlinefull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelonlinefull.py" title="27 September 2022 07:46:30 PM">19</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novels.pl/" target="_blank">https://novels.pl/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelspl.py" title="18 January 2023 10:47:05 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsala.com/" target="_blank">https://novelsala.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelsala.py" title="27 September 2022 09:18:35 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsemperor.com/" target="_blank">https://novelsemperor.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelsemperor.py" title="10 October 2022 04:20:28 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsite.net/" target="_blank">https://novelsite.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelsite.py" title="27 September 2022 08:36:43 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsonline.net/" target="_blank">https://novelsonline.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelsonline.py" title="27 September 2022 08:36:43 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltranslate.com/" target="_blank">https://noveltranslate.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/noveltranslate.py" title="02 November 2022 08:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelww.com/" target="_blank">https://novelww.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelww.py" title="02 October 2022 08:48:50 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelzec.com/" target="_blank">https://novelzec.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelzec.py" title="27 September 2022 07:22:47 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://pandanovel.org/" target="_blank">https://pandanovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/p/pandanovelorg.py" title="02 February 2023 03:23:41 AM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://pianmanga.com/" target="_blank">https://pianmanga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/p/pianmanga.py" title="27 September 2022 08:34:44 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://puretl.com/" target="_blank">https://puretl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/p/puretl.py" title="09 December 2022 01:10:58 AM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://randomnovel.com/" target="_blank">https://randomnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/randomnovel.py" title="02 October 2022 08:48:50 PM">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobes.net/" target="_blank">https://ranobes.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/ranobes.py" title="03 October 2022 11:27:34 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://re-library.com/" target="_blank">https://re-library.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/relibrary.py" title="24 November 2022 04:30:35 AM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readlightnovel.me/" target="_blank">https://readlightnovel.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readlightnovelorg.py" title="27 September 2022 07:22:47 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readlightnovels.net/" target="_blank">https://readlightnovels.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readlightnovelsnet.py" title="08 October 2022 12:01:06 AM">32</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://readmanganato.com/" target="_blank">https://readmanganato.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readmanganato.py" title="14 December 2022 04:17:52 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readmtl.com/" target="_blank">https://readmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readmtl.py" title="10 October 2022 07:53:33 PM">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readnovelfull.com/" target="_blank">https://readnovelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readnovelfull.py" title="04 October 2022 12:43:55 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readonlinenovels.com/" target="_blank">https://readonlinenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readonlinenovels.py" title="04 November 2022 02:46:53 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/amritoo"><img src="https://avatars.githubusercontent.com/u/45586379?v=4&s=24" alt="amritoo" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readwebnovels.net/" target="_blank">https://readwebnovels.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readwebnovels.py" title="27 September 2022 08:36:43 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://reaperscans.com/" target="_blank">https://reaperscans.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/reaperscans.py" title="27 September 2022 07:22:47 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://reincarnationpalace.com/" target="_blank">https://reincarnationpalace.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/reincarnationpalace.py" title="27 September 2022 09:18:35 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rpgnoob.wordpress.com/" target="_blank">https://rpgnoob.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/rpgnovels.py" title="27 September 2022 07:22:47 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rpgnovels.com/" target="_blank">https://rpgnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/rpgnovels.py" title="27 September 2022 07:22:47 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://scribblehub.com/" target="_blank">https://scribblehub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/scribblehub.py" title="03 October 2022 07:16:22 AM">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/Epicpkmn11"><img src="https://avatars.githubusercontent.com/u/41608708?v=4&s=24" alt="Epicpkmn11" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://secondlifetranslations.com/" target="_blank">https://secondlifetranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/secondlifetranslations.py" title="15 September 2022 08:14:58 AM">5</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://shalvationtranslations.wordpress.com/" target="_blank">https://shalvationtranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/shalvation.py" title="27 September 2022 08:36:43 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://skydemonorder.com/" target="_blank">https://skydemonorder.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/skydemonorder.py" title="16 May 2023 11:05:45 PM">4</a></td>
<td></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://skynovel.org/" target="_blank">https://skynovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/skynovel.py" title="27 September 2022 08:36:43 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://sleepytranslations.com/" target="_blank">https://sleepytranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/sleepytrans.py" title="27 September 2022 07:22:47 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://smnovels.com/" target="_blank">https://smnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/smnovels.py" title="27 September 2022 07:22:47 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://snowycodex.com/" target="_blank">https://snowycodex.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/snowycodex.py" title="07 October 2022 06:54:57 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://steambunlightnovel.com/" target="_blank">https://steambunlightnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/steambun.py" title="27 September 2022 07:22:47 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://supernovel.net/" target="_blank">https://supernovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/supernovel.py" title="27 September 2022 07:22:47 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://systemtranslation.com/" target="_blank">https://systemtranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/systemtranslation.py" title="10 October 2022 04:33:21 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tamagotl.com/" target="_blank">https://tamagotl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/tamagotl.py" title="10 October 2022 03:39:48 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tipnovel.com/" target="_blank">https://tipnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/tipnovel.py" title="27 September 2022 07:22:47 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://toc.qidianunderground.org/" target="_blank">https://toc.qidianunderground.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/q/qidianunderground.py" title="03 October 2022 11:27:34 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/BorgSquared"><img src="https://avatars.githubusercontent.com/u/7807834?v=4&s=24" alt="BorgSquared" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tocqidianunderground.blogspot.com/" target="_blank">https://tocqidianunderground.blogspot.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/q/qidianunderground.py" title="03 October 2022 11:27:34 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/BorgSquared"><img src="https://avatars.githubusercontent.com/u/7807834?v=4&s=24" alt="BorgSquared" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tomotranslations.com/" target="_blank">https://tomotranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/tomotrans.py" title="27 September 2022 08:36:43 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://toonily.com/" target="_blank">https://toonily.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/toonily.py" title="27 September 2022 08:34:44 PM">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://totallytranslations.com/" target="_blank">https://totallytranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/totallytranslations.py" title="27 September 2022 08:36:43 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://travistranslations.com/" target="_blank">https://travistranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/travistranslations.py" title="27 September 2022 07:22:47 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://usefulnovel.com/" target="_blank">https://usefulnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/u/usefulnovel.py" title="02 October 2022 08:48:50 PM">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://veratales.com/" target="_blank">https://veratales.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/v/veratales.py" title="27 September 2022 08:36:43 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://vipnovel.com/" target="_blank">https://vipnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/v/vipnovel.py" title="27 September 2022 07:22:47 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://vistranslations.wordpress.com/" target="_blank">https://vistranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/v/vistrans.py" title="27 September 2022 08:36:43 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wanderinginn.com/" target="_blank">https://wanderinginn.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wanderinginn.py" title="27 September 2022 07:22:47 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelonline.com/" target="_blank">https://webnovelonline.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/webnovelonlinecom.py" title="27 September 2022 07:22:47 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelonline.net/" target="_blank">https://webnovelonline.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/webnovelonlinenet.py" title="04 November 2022 03:06:07 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://whatsawhizzerwebnovels.com/" target="_blank">https://whatsawhizzerwebnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/whatsawhizzerwebnovels.py" title="27 September 2022 06:29:20 PM">1</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wnmtl.org/" target="_blank">https://wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wnmtl.py" title="02 October 2022 08:48:50 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wondernovels.com/" target="_blank">https://wondernovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wondernovels.py" title="27 September 2022 08:36:43 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://woopread.com/" target="_blank">https://woopread.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/woopread.py" title="27 September 2022 08:36:43 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wordexcerpt.com/" target="_blank">https://wordexcerpt.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wordexcerpt.py" title="27 September 2022 08:36:43 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wordrain69.com/" target="_blank">https://wordrain69.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wordrain.py" title="27 September 2022 09:18:35 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://wto.to/" target="_blank">https://wto.to/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/bato.py" title="25 September 2022 08:00:08 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wujizun.com/" target="_blank">https://wujizun.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wujizun.py" title="27 September 2022 07:22:47 PM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxia.city/" target="_blank">https://wuxia.city/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiacity.py" title="02 October 2022 08:48:50 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.name/" target="_blank">https://wuxiaworld.name/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiaworldio.py" title="27 September 2022 07:22:47 PM">25</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.online/" target="_blank">https://wuxiaworld.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiaonline.py" title="27 September 2022 08:36:43 PM">29</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworldsite.co/" target="_blank">https://wuxiaworldsite.co/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiaworldsite.py" title="27 September 2022 07:22:47 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.allnovel.org/" target="_blank">https://www.allnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/allnovel.py" title="04 October 2022 08:04:38 PM">47</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.asianhobbyist.com/" target="_blank">https://www.asianhobbyist.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/a/asianhobbyist.py" title="08 October 2022 07:45:40 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.blackbox-tl.com/" target="_blank">https://www.blackbox-tl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/blackboxtl.py" title="27 September 2022 07:22:47 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.box-novel.com/" target="_blank">https://www.box-novel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/b/boxnovelcom.py" title="27 September 2022 08:36:43 PM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.chickengege.org/" target="_blank">https://www.chickengege.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/c/chickengege.py" title="29 September 2022 08:52:45 PM">4</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.divinedaolibrary.com/" target="_blank">https://www.divinedaolibrary.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/d/divinedaolibrary.py" title="27 September 2022 07:22:47 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.f-w-o.com/" target="_blank">https://www.f-w-o.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fantasyworldonline.py" title="27 September 2022 07:22:47 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fanfiction.net/" target="_blank">https://www.fanfiction.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fanfiction.py" title="27 September 2022 07:22:47 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fictionpress.com/" target="_blank">https://www.fictionpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fictionpress.py" title="27 September 2022 07:22:47 PM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.flying-lines.com/" target="_blank">https://www.flying-lines.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/flyinglines.py" title="27 September 2022 07:22:47 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.foxteller.com/" target="_blank">https://www.foxteller.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/foxteller.py" title="27 September 2022 07:22:47 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.freelightnovel.com/" target="_blank">https://www.freelightnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/freelightnovel.py" title="27 September 2022 07:22:47 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fringecapybara.com/" target="_blank">https://www.fringecapybara.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fringecapybara.py" title="27 September 2022 07:22:47 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fuyuneko.org/" target="_blank">https://www.fuyuneko.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/f/fuyuneko.py" title="27 September 2022 07:22:47 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.inkitt.com/" target="_blank">https://www.inkitt.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/inkitt.py" title="28 September 2022 02:22:36 PM">2</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.isotls.com/" target="_blank">https://www.isotls.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/i/isotls.py" title="08 September 2022 05:57:51 PM">59</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.kitenovel.com/" target="_blank">https://www.kitenovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/k/kitenovel.py" title="27 September 2022 07:22:47 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.koreanmtl.online/" target="_blank">https://www.koreanmtl.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/k/koreanmtl.py" title="02 October 2022 08:48:50 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelmeta.com/" target="_blank">https://www.lightnovelmeta.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelmeta.py" title="25 September 2022 04:31:03 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelpub.com/" target="_blank">https://www.lightnovelpub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelpub.py" title="10 December 2022 10:50:11 PM">26</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelreader.me/" target="_blank">https://www.lightnovelreader.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelreader.py" title="27 January 2023 08:37:27 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelworld.com/" target="_blank">https://www.lightnovelworld.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelworld.com.py" title="10 December 2022 10:50:11 PM">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lnreader.org/" target="_blank">https://www.lnreader.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/lightnovelreader.py" title="27 January 2023 08:37:27 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ltnovel.com/" target="_blank">https://www.ltnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/l/ltnovel.py" title="25 September 2022 02:31:03 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.machine-translation.org/" target="_blank">https://www.machine-translation.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/machinetransorg.py" title="02 October 2022 08:48:50 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.mangaread.org/" target="_blank">https://www.mangaread.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangaread.py" title="04 November 2022 02:39:25 PM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.mangaweebs.in/" target="_blank">https://www.mangaweebs.in/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mangaweebs.py" title="27 September 2022 08:34:44 PM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.miraslation.net/" target="_blank">https://www.miraslation.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/miraslation.py" title="21 September 2022 05:54:36 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlnation.com/" target="_blank">https://www.mtlnation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mtlnation.py" title="24 November 2022 12:39:06 AM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlreader.com/" target="_blank">https://www.mtlreader.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/m/mtlreader.py" title="02 October 2022 08:48:50 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.neosekaitranslations.com/" target="_blank">https://www.neosekaitranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/neosekaitranslations.py" title="27 September 2022 08:36:43 PM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.newsnovel.net/" target="_blank">https://www.newsnovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/newsnovel.py" title="27 September 2022 08:36:43 PM">30</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelall.com/" target="_blank">https://www.novelall.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelall.py" title="27 September 2022 07:46:30 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.novelcool.com/" target="_blank">https://www.novelcool.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelcool.py" title="08 November 2022 05:40:00 AM">33</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelhall.com/" target="_blank">https://www.novelhall.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelhall.py" title="02 October 2022 08:48:50 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelhunters.com/" target="_blank">https://www.novelhunters.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelhunters.py" title="27 September 2022 09:18:35 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmt.com/" target="_blank">https://www.novelmt.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelmt.py" title="02 October 2022 08:48:50 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmtl.com/" target="_blank">https://www.novelmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelmtl.py" title="02 October 2022 08:48:50 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmultiverse.com/" target="_blank">https://www.novelmultiverse.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelmultiverse.py" title="27 September 2022 07:22:47 PM">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelpassion.com/" target="_blank">https://www.novelpassion.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelpassion.py" title="27 September 2022 07:22:47 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelpub.com/" target="_blank">https://www.novelpub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelpub.py" title="10 December 2022 10:50:11 PM">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novels.pl/" target="_blank">https://www.novels.pl/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelspl.py" title="18 January 2023 10:47:05 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelupdates.cc/" target="_blank">https://www.novelupdates.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/n/novelupdatescc.py" title="09 October 2022 02:28:43 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.oppatranslations.com/" target="_blank">https://www.oppatranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/o/oppatrans.py" title="27 September 2022 08:36:43 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ornovel.com/" target="_blank">https://www.ornovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/o/ornovel.py" title="27 September 2022 08:36:43 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.pandamanga.xyz/" target="_blank">https://www.pandamanga.xyz/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/p/pandamanga.py" title="10 October 2022 04:20:28 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.cc/" target="_blank">https://www.readlightnovel.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readlightnovelcc.py" title="27 September 2022 08:36:43 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.me/" target="_blank">https://www.readlightnovel.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readlightnovelorg.py" title="27 September 2022 07:22:47 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readwn.com/" target="_blank">https://www.readwn.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/readwn.py" title="02 October 2022 08:48:50 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.royalroad.com/" target="_blank">https://www.royalroad.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/r/royalroad.py" title="28 March 2023 07:58:15 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Epicpkmn11"><img src="https://avatars.githubusercontent.com/u/41608708?v=4&s=24" alt="Epicpkmn11" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.scribblehub.com/" target="_blank">https://www.scribblehub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/s/scribblehub.py" title="03 October 2022 07:16:22 AM">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/Epicpkmn11"><img src="https://avatars.githubusercontent.com/u/41608708?v=4&s=24" alt="Epicpkmn11" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.tapread.com/" target="_blank">https://www.tapread.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/tapread.py" title="27 September 2022 07:22:47 PM">57</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.teanovel.com/" target="_blank">https://www.teanovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/teanovel.py" title="30 September 2022 12:16:30 PM">2</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.teanovel.net/" target="_blank">https://www.teanovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/teanovel.py" title="30 September 2022 12:16:30 PM">2</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.topmanhua.com/" target="_blank">https://www.topmanhua.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/t/topmanhua.py" title="27 September 2022 07:22:47 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.virlyce.com/" target="_blank">https://www.virlyce.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/v/virlyce.py" title="27 September 2022 08:36:43 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.volarenovels.com/" target="_blank">https://www.volarenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/v/volarenovels.py" title="27 September 2022 08:36:43 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovel.com/" target="_blank">https://www.webnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/webnovel.py" title="10 October 2022 09:54:59 AM">89</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovelpub.com/" target="_blank">https://www.webnovelpub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/webnovelpub.py" title="10 December 2022 10:50:11 PM">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wnmtl.org/" target="_blank">https://www.wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wnmtl.py" title="02 October 2022 08:48:50 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxia.blog/" target="_blank">https://www.wuxia.blog/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiablog.py" title="29 September 2022 03:20:25 PM">4</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiahub.com/" target="_blank">https://www.wuxiahub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiahub.py" title="01 October 2022 06:45:12 AM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxialeague.com/" target="_blank">https://www.wuxialeague.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxialeague.py" title="27 September 2022 08:36:43 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiamtl.com/" target="_blank">https://www.wuxiamtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiamtl.py" title="02 October 2022 08:48:50 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxianovelhub.com/" target="_blank">https://www.wuxianovelhub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxianovelhub.py" title="25 September 2022 02:31:03 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiapub.com/" target="_blank">https://www.wuxiapub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiapub.py" title="01 October 2022 06:45:12 AM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiar.com/" target="_blank">https://www.wuxiar.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiar.py" title="25 September 2022 02:31:03 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiau.com/" target="_blank">https://www.wuxiau.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiau.py" title="01 October 2022 06:45:12 AM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiav.com/" target="_blank">https://www.wuxiav.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiav.py" title="25 September 2022 02:31:03 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiaworld.com/" target="_blank">https://www.wuxiaworld.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiacom.py" title="09 December 2022 01:10:58 AM">90</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiax.com/" target="_blank">https://www.wuxiax.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiax.py" title="25 September 2022 02:31:03 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiaz.com/" target="_blank">https://www.wuxiaz.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/w/wuxiaz.py" title="01 October 2022 06:45:12 AM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.xiainovel.com/" target="_blank">https://www.xiainovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/x/xiainovel.py" title="27 September 2022 08:36:43 PM">57</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://zetrotranslation.com/" target="_blank">https://zetrotranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/z/zetrotranslation.py" title="30 September 2022 02:34:32 AM">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://zinmanga.com/" target="_blank">https://zinmanga.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/z/zinmanga.py" title="02 October 2022 08:48:50 PM">77</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://zinnovel.com/" target="_blank">https://zinnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/en/z/zinnovel.py" title="27 September 2022 07:22:47 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
</tbody>
</table>


### `es` Spanish; Castilian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://cclawtranslations.home.blog/" target="_blank">https://cclawtranslations.home.blog/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/es/domentranslations.py" title="27 September 2022 07:22:47 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://domentranslations.wordpress.com/" target="_blank">https://domentranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/es/domentranslations.py" title="27 September 2022 07:22:47 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
</tbody>
</table>


### `fr` French

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://anime-sama.fr/" target="_blank">https://anime-sama.fr/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/fr/animesama.py" title="20 April 2023 03:21:52 AM">4</a></td>
<td><a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://chireads.com/" target="_blank">https://chireads.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/fr/chireads.py" title="29 January 2023 03:56:00 AM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelfr.com/" target="_blank">https://lightnovelfr.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/fr/lightnovelfr.py" title="10 October 2022 04:27:39 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lnmtlfr.com/" target="_blank">https://lnmtlfr.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/fr/lnmtlfr.py" title="09 April 2023 12:16:59 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://xiaowaz.fr/" target="_blank">https://xiaowaz.fr/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/fr/xiaowaz.py" title="29 September 2022 11:43:13 AM">3</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
</tbody>
</table>


### `id` Indonesian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zhi-end.blogspot.co.id/" target="_blank">http://zhi-end.blogspot.co.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/zhiend.py" title="27 September 2022 08:36:43 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zhi-end.blogspot.com/" target="_blank">http://zhi-end.blogspot.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/zhiend.py" title="27 September 2022 08:36:43 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://darktranslation.com/" target="_blank">https://darktranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/darktrans.py" title="27 September 2022 08:36:43 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://grensia.blogspot.com/" target="_blank">https://grensia.blogspot.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/grensia_blogspot.py" title="27 September 2022 08:36:43 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://indowebnovel.id/" target="_blank">https://indowebnovel.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/indowebnovel.py" title="28 April 2023 09:14:46 AM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://meionovel.id/" target="_blank">https://meionovel.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/meionovel.py" title="27 September 2022 08:36:43 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://morenovel.net/" target="_blank">https://morenovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/morenovel.py" title="02 October 2022 10:55:54 AM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelgo.id/" target="_blank">https://novelgo.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/novelgo.py" title="27 September 2022 07:22:47 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a> <a href="https://github.com/dragonroad99"><img src="https://avatars.githubusercontent.com/u/22253628?v=4&s=24" alt="dragonroad99" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelku.id/" target="_blank">https://novelku.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/novelku.py" title="28 May 2023 01:55:20 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelringan.com/" target="_blank">https://novelringan.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/novelringan.py" title="27 September 2022 08:36:43 PM">59</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltoon.mobi/" target="_blank">https://noveltoon.mobi/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/noveltoon.py" title="01 October 2022 06:53:45 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wbnovel.com/" target="_blank">https://wbnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/wbnovel.py" title="27 September 2022 08:36:43 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelindonesia.com/" target="_blank">https://webnovelindonesia.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/webnovelindonesia.py" title="27 September 2022 08:36:43 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.idqidian.us/" target="_blank">https://www.idqidian.us/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/idqidian.py" title="27 September 2022 09:18:35 PM">46</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovelover.com/" target="_blank">https://www.webnovelover.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/webnovelover.py" title="03 October 2022 11:27:34 PM">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.worldnovel.online/" target="_blank">https://www.worldnovel.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/worldnovelonline.py" title="27 September 2022 07:22:47 PM">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://yukinovel.id/" target="_blank">https://yukinovel.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/yukinovel.py" title="27 September 2022 08:36:43 PM">56</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://yukinovel.me/" target="_blank">https://yukinovel.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/id/yukinovel.py" title="27 September 2022 08:36:43 PM">56</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
</tbody>
</table>


### `pt` Portuguese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://blnovels.net/" target="_blank">https://blnovels.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/pt/blnovels.py" title="27 September 2022 07:22:47 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://centralnovel.com/" target="_blank">https://centralnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/pt/centralnovel.py" title="04 November 2022 03:14:15 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ceunovel.com/" target="_blank">https://www.ceunovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/pt/ceunovel.py" title="19 September 2022 08:30:30 AM">1</a></td>
<td><a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
</tbody>
</table>


### `ru` Russian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://bestmanga.club/" target="_blank">https://bestmanga.club/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/ru/bestmanga.py" title="24 September 2022 11:12:30 AM">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jaomix.ru/" target="_blank">https://jaomix.ru/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/ru/jaomix.py" title="02 February 2023 03:47:12 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://litnet.com/" target="_blank">https://litnet.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/ru/litnet.py" title="03 October 2022 11:27:34 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `vi` Vietnamese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://docln.net/" target="_blank">https://docln.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/vi/lnhakone.py" title="03 October 2022 11:27:34 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ln.hako.vn/" target="_blank">https://ln.hako.vn/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/vi/lnhakone.py" title="03 October 2022 11:27:34 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://truyenfull.vn/" target="_blank">https://truyenfull.vn/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/vi/truenfull.py" title="02 October 2022 08:48:50 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://truyentr.info/" target="_blank">https://truyentr.info/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/vi/truenfull.py" title="02 October 2022 08:48:50 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `zh` Chinese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://sj.uukanshu.com/" target="_blank">https://sj.uukanshu.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/zh/uukanshu.py" title="27 September 2022 08:36:43 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tw.m.ixdzs.com/" target="_blank">https://tw.m.ixdzs.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/zh/ixdzs.py" title="27 September 2022 07:22:47 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/junqili259"><img src="https://avatars.githubusercontent.com/u/39481617?v=4&s=24" alt="junqili259" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.aixdzs.com/" target="_blank">https://www.aixdzs.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/zh/aixdzs.py" title="27 September 2022 08:36:43 PM">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.daocaorenshuwu.com/" target="_blank">https://www.daocaorenshuwu.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/zh/daocaorenshuwu.py" title="27 September 2022 08:36:43 PM">58</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.soxs.cc/" target="_blank">https://www.soxs.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/e2152147e9d37929ef6fd72e1c9937bf2838a4ce/sources/zh/soxs.py" title="27 September 2022 07:22:47 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/junqili259"><img src="https://avatars.githubusercontent.com/u/39481617?v=4&s=24" alt="junqili259" height="24"/></a></td>
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
<tr><td><a href="http://boxnovel.org/" target="_blank">http://boxnovel.org/</a></td>
<td>No longer operational</td>
</tr>
<tr><td><a href="http://fullnovel.live/" target="_blank">http://fullnovel.live/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="http://gravitytales.com/" target="_blank">http://gravitytales.com/</a></td>
<td>Domain is expired</td>
</tr>
<tr><td><a href="http://hs2ppe.co.uk/" target="_blank">http://hs2ppe.co.uk/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="http://wspadancewichita.com/" target="_blank">http://wspadancewichita.com/</a></td>
<td>Site closed and moved to https://readnovelfull.com/</td>
</tr>
<tr><td><a href="http://www.hanyunovels.site/" target="_blank">http://www.hanyunovels.site/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://4scanlation.com/" target="_blank">https://4scanlation.com/</a></td>
<td>Domain expired</td>
</tr>
<tr><td><a href="https://888novel.com/" target="_blank">https://888novel.com/</a></td>
<td>Gets IP banned for using crawler</td>
</tr>
<tr><td><a href="https://anythingnovel.com/" target="_blank">https://anythingnovel.com/</a></td>
<td>The domain is for sale</td>
</tr>
<tr><td><a href="https://arangscans.com/" target="_blank">https://arangscans.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://bestoflightnovels.com/" target="_blank">https://bestoflightnovels.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://boxnovel.online/" target="_blank">https://boxnovel.online/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://boxnovel.org/" target="_blank">https://boxnovel.org/</a></td>
<td>No longer operational</td>
</tr>
<tr><td><a href="https://clicknovel.net/" target="_blank">https://clicknovel.net/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://dsrealmtranslations.com/" target="_blank">https://dsrealmtranslations.com/</a></td>
<td>Domain expired</td>
</tr>
<tr><td><a href="https://fsapk.com/" target="_blank">https://fsapk.com/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="https://indomtl.com/" target="_blank">https://indomtl.com/</a></td>
<td>Not crawler friendly</td>
</tr>
<tr><td><a href="https://instadoses.com/" target="_blank">https://instadoses.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://kiss-novel.com/" target="_blank">https://kiss-novel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://light-novel.online/" target="_blank">https://light-novel.online/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://lightnovel.tv/" target="_blank">https://lightnovel.tv/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://lightnovelkiss.com/" target="_blank">https://lightnovelkiss.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://lightnovelshub.com/" target="_blank">https://lightnovelshub.com/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="https://mtled-novels.com/" target="_blank">https://mtled-novels.com/</a></td>
<td>Domain is expired</td>
</tr>
<tr><td><a href="https://myoniyonitranslations.com/" target="_blank">https://myoniyonitranslations.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://newsite.kolnovel.com/" target="_blank">https://newsite.kolnovel.com/</a></td>
<td>Site is down</td>
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
<tr><td><a href="https://novelsrock.com/" target="_blank">https://novelsrock.com/</a></td>
<td>Web server is down</td>
</tr>
<tr><td><a href="https://omgnovels.com/" target="_blank">https://omgnovels.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://overabook.com/" target="_blank">https://overabook.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://pery.info/" target="_blank">https://pery.info/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://read.asianovel.com/" target="_blank">https://read.asianovel.com/</a></td>
<td>Connection timed out</td>
</tr>
<tr><td><a href="https://readnovelz.net/" target="_blank">https://readnovelz.net/</a></td>
<td>Redirects to webnovelonline.net</td>
</tr>
<tr><td><a href="https://tunovelaligera.com/" target="_blank">https://tunovelaligera.com/</a></td>
<td>Broken. Chapters does not load</td>
</tr>
<tr><td><a href="https://viewnovel.net/" target="_blank">https://viewnovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://wordexcerpt.org/" target="_blank">https://wordexcerpt.org/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://writerupdates.com/" target="_blank">https://writerupdates.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://wuxiaworld.io/" target="_blank">https://wuxiaworld.io/</a></td>
<td>Cloudflare Error 522, can not connect to host</td>
</tr>
<tr><td><a href="https://wuxiaworld.live/" target="_blank">https://wuxiaworld.live/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://wuxiaworld.site/" target="_blank">https://wuxiaworld.site/</a></td>
<td>Access denied</td>
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
<td>Redrects to https://foxteller.com/</td>
</tr>
<tr><td><a href="https://www.shinsori.com/" target="_blank">https://www.shinsori.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://www.translateindo.com/" target="_blank">https://www.translateindo.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiaworld.co/" target="_blank">https://www.wuxiaworld.co/</a></td>
<td>This site can not be reached</td>
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

## Sponsors

<table>
  <tbody>
    <tr align="center">
      <td align="center"><a href="https://wuxiaworld.eu"><img src="https://www.wuxiaworld.eu/apple-touch-icon.png" width="200px;" alt=""/><br /><sub><h3>Wuxiaworld</b></sub></a></td>
    </tr>
  </tbody>
</table>