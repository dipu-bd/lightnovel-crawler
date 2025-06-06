# Lightnovel Crawler

[![download win](https://img.shields.io/badge/download-lncrawl.exe-red?logo=windows&style=for-the-badge)](https://go.bitanon.dev/lncrawl-windows)
[![download linux](<https://img.shields.io/badge/download-lncrawl_(linux)-brown?logo=linux&style=for-the-badge>)](https://go.bitanon.dev/lncrawl-linux)
[![download mac](<https://img.shields.io/badge/download-lncrawl_(mac)-blue?logo=apple&style=for-the-badge>)](https://go.bitanon.dev/lncrawl-mac)
<br>
[![Discord](https://img.shields.io/discord/578550900231110656?logo=discord&label=discord)](https://discord.gg/wMECG2Q)
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg?logo=python)](https://pypi.org/project/lightnovel-crawler)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/dipu-bd/lightnovel-crawler/blob/master/LICENSE)
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
    - [Login to www.wuxiaworld.com](#login-to-wwwwuxiaworldcom)
  - [Development](#development)
    - [Adding new source](#adding-new-source)
    - [Adding new Bot](#adding-new-bot)
  - [Supported sources](#supported-sources)
    - [`~` Unknown](#-unknown)
    - [`ar` Arabic](#ar-arabic)
    - [`en` English](#en-english)
    - [`es` Spanish; Castilian](#es-spanish-castilian)
    - [`fr` French](#fr-french)
    - [`id` Indonesian](#id-indonesian)
    - [`pt` Portuguese](#pt-portuguese)
    - [`ru` Russian](#ru-russian)
    - [`vi` Vietnamese](#vi-vietnamese)
    - [`zh` Chinese](#zh-chinese)
  - [Rejected sources](#rejected-sources)
  - [Supported output formats](#supported-output-formats)
  - [Sponsors](#sponsors)

<a href="https://github.com/dipu-bd/lightnovel-crawler"><img src="res/lncrawl-icon.png" width="128px" align="right"/></a>

## Installation

**This application uses _Calibre_ to convert ebooks.** <br>
**Install it from https://calibre-ebook.com/download** <br>
Without it, you will only get output in epub, text, and web formats. <br>

**For macOS, you need to manually add the path to Calibre.** <br>
Before starting lncrawl, use the command:

```bash
$ export PATH="$PATH:/Applications/calibre.app/Contents/MacOS"
```

If you used a folder other than Applications during installation, replace `/Applications/` with your path to Calibre.

<!-- Also, you have to install **node.js** to access cloudflare enabled sites (e.g. https://novelplanet.com/). Download and install node.js from here: https://nodejs.org/en/download/ -->

<!-- brew install python-tk -->

### Standalone Bundle (Windows, Linux)

⏬ **Windows**: [lncrawl.exe ~ 36MB](https://go.bitanon.dev/lncrawl-windows)

> In Windows 8, 10 or later versions, it might say that `lncrawl.exe` is not safe to dowload or execute. You should bypass/ignore this security check to execute this program.

⏬ **Linux**: [lncrawl ~ 54MB](https://go.bitanon.dev/lncrawl-linux)

> It is recommended to install via **pip** if you are on Linux

⏬ **MacOS**: [lncrawl ~ 33MB](https://go.bitanon.dev/lncrawl-mac)

> It is recommended to install via **pip** if you are on Mac

⏬ _To get older versions visit the [Releases page](https://github.com/dipu-bd/lightnovel-crawler/releases)_

### PIP (Windows, Mac, and Linux)

📦 A python package named `lightnovel-crawler` is available at [pypi](https://pypi.org/project/lightnovel-crawler).

> Make sure you have installed **Python v3.8** or higher and have **pip** enabled. Visit these links to install python with pip in [Windows](https://stackoverflow.com/a/44437176/1583052), [Linux](https://stackoverflow.com/a/51799221/1583052) and [MacOS](https://itsevans.com/install-pip-osx/). Feel free to ask on the Discord server if you are stuck.

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
$ docker build -t lncrawl -f Dockerfile .
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

- Install [Termux](https://github.com/termux/termux-app/releases/) from github.
- Open the app and run these commands one by one:
  - `termux-change-repo && pkg upgrade -y && termux-setup-storage` run to update repo to local and setup storage
  - `pkg upgrade -y && pkg install python-grpcio python-lxml python-pillow -y` run to setup depends
  - `CFLAGS="-Wno-error=incompatible-function-pointer-types" pip install -U setuptools lightnovel-crawler` run to install
  - `cd ~/storage/downloads` set storage location to downloads folder
  - `lncrawl` run the crawler
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

- Run the program (use python v3.8 or higher):

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
╱╱╱╱╱╭━╯┃ v3.9.4
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
  -b {console,telegram,discord,lookup,server}, --bot {console,telegram,discord,lookup,server}
                        Select a bot. Default: console.
  --shard-id [SHARD_ID]
                        Discord bot shard id (default: 0)
  --shard-count [SHARD_COUNT]
                        Discord bot shard counts (default: 1)
  --selenium-grid URL   Selenium Grid URL for Chrome Webdriver
  --host HOSTNAME       Server host name. Default: 0.0.0.0
  --port PORT           Server port. Default: 8080
  --watch               Run server in watch mode
  --suppress            Suppress all input prompts and use defaults.
  --ignore-images       Ignore images in chapters when downloading.
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

We are supporting 0 sources and 0 crawlers.<!-- auto generated supported sources list -->

## Rejected sources

<!-- auto generated rejected sources list -->

<table>
<tbody>
<tr><th>Source URL</th>
<th>Rejection Cause</th>
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
- RB
- SNB
- TCR

## Sponsors

<table>
  <tbody>
    <tr align="center">
      <td align="center"><a href="https://wuxiaworld.eu"><img src="https://www.wuxiaworld.eu/apple-touch-icon.png" width="200px;" alt=""/><br /><sub><h3>Wuxiaworld</b></sub></a></td>
    </tr>
  </tbody>
</table>
