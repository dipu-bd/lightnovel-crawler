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
$ pip install -U lightnovel-crawler
```

In some cases you have to use `python3 -m pip` or `pip3` or `python -m pip`. And you do not need `--user` option, if you are running from root.

Next, open your terminal and enter:

```
$ lncrawl
```

> To view extra logs, use: `lncrawl -lll`

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
$ docker run -v ~/Lightnovels:/app/Lightnovels -it lncrawl
```

> You can setup _alias_ to the above command in your terminal's profile to run using single a single-word command.

### Termux (Android)

> Please read before proceeding:
> - It is not guaranteed that the app will run smoothly in all devices.
> - It may take a long time to install depending on your mobile processor.
> - It is recommended to use the bots on either Discord or Telegram if you are on mobile.

📱 Using Termux, you can run this app in your android phones too. Follow this instructions:

- Install [Termux](https://play.google.com/store/apps/details?id=com.termux) from playstore.
- Open the app and run these commands one by one:
  - `pkg upgrade`
  - `pkg install python libxml2 libxslt libjpeg-turbo`
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
╱╱╱╱╱╭━╯┃ v2.30.0
╱╱╱╱╱╰━━╯ 🔗 https://github.com/dipu-bd/lightnovel-crawler
--------------------------------------------------------------------------------
usage: lncrawl [options...]
       lightnovel-crawler [options...]

optional arguments:
  -h, --help            show this help message and exit

  -v, --version         show program's version number and exit
  -l                    Set log levels. (-l = warn, -ll = info, -lll = debug).
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
  --page START STOP.    The start and final chapter urls.
  --range FROM TO.      The start and final chapter indexes.
  --volumes [N ...]     The list of volume numbers to download.
  --chapters [URL ...]  A list of specific chapter urls.
  --bot {console,telegram,discord,test}
                        Select a bot. Default: console.
  --shard-id [SHARD_ID]
                        Discord bot shard id (default: 0)
  --shard-count [SHARD_COUNT]
                        Discord bot shard counts (default: 1)
  --suppress            Suppress all input prompts and use defaults.
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

## Development

You are very welcome to contribute in this project. You can:

- create new issues pointing out the bugs.
- solve existing issues.
- add your own sources.
- add new output formats.
- create new bots.

### Adding new source

- Create new crawler using the [`sources/_template.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/_template.py) as template. Read the comments on the file for instructions.
- You can find plenty examples in the `sources` folder.
- Put your source file inside the language folder. The `en` folder has too many files, therefore it is grouped using the first letter of the domain name.

### Adding new Bot

- Create a new bot file using [`bots/_sample.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/_sample.py) as template.
- Import bot to [`bots/__init__.py`](https://github.com/dipu-bd/lightnovel-crawler/blob/master/lncrawl/bots/__init__.py) file.

## Supported sources

> Request new one by [creating a new issue](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose).

<!-- auto generated supported sources list -->

We are supporting 213 sources and 227 crawlers.

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
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/ar/arnovel.py" title="22 March 2022 02:50:32 PM">20</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
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
<td><a href="http://boxnovel.org/" target="_blank">http://boxnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/boxnovelorg.py" title="22 March 2022 02:50:32 PM">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://hs2ppe.co.uk/" target="_blank">http://hs2ppe.co.uk/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/h/hs2ppe.py" title="22 March 2022 02:50:32 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://novelfull.com/" target="_blank">http://novelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelfull.py" title="22 March 2022 02:50:32 PM">44</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://ranobes.net/" target="_blank">http://ranobes.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/ranobes.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://readonlinenovels.com/" target="_blank">http://readonlinenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readonlinenovels.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/amritoo"><img src="https://avatars.githubusercontent.com/u/45586379?v=4&s=24" alt="amritoo" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://wnmtl.org/" target="_blank">http://wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wnmtl.py" title="22 March 2022 09:23:50 AM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://wspadancewichita.com/" target="_blank">http://wspadancewichita.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wspadancewichita.py" title="22 March 2022 02:50:32 PM">26</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.fujitranslation.com/" target="_blank">http://www.fujitranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fujitrans.py" title="22 March 2022 02:50:32 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.wnmtl.org/" target="_blank">http://www.wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wnmtl.py" title="22 March 2022 09:23:50 AM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zenithnovels.com/" target="_blank">http://zenithnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/z/zenithnovels.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://1stkissnovel.love/" target="_blank">https://1stkissnovel.love/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/0/1stkissnovel.py" title="22 March 2022 02:50:32 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/mchubby"><img src="https://avatars.githubusercontent.com/u/1490889?v=4&s=24" alt="mchubby" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://88tangeatdrinkread.wordpress.com/" target="_blank">https://88tangeatdrinkread.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/0/88tang.py" title="22 March 2022 02:50:32 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://allnovel.org/" target="_blank">https://allnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/allnovel.py" title="22 March 2022 02:50:32 PM">38</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://amnesiactl.com/" target="_blank">https://amnesiactl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/amnesiactl.py" title="22 March 2022 02:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://arangscans.com/" target="_blank">https://arangscans.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/arangscans.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://asadatranslations.com/" target="_blank">https://asadatranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/asadatrans.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://automtl.wordpress.com/" target="_blank">https://automtl.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/automtl.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://babelnovel.com/" target="_blank">https://babelnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/babelnovel.py" title="22 March 2022 02:50:32 PM">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bakapervert.wordpress.com/" target="_blank">https://bakapervert.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/bakapervert.py" title="30 March 2022 12:22:50 AM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bestlightnovel.com/" target="_blank">https://bestlightnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/bestlightnovel.py" title="22 March 2022 02:50:32 PM">19</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://booknet.com/" target="_blank">https://booknet.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/booknet.py" title="22 March 2022 02:50:32 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://boxnovel.com/" target="_blank">https://boxnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/boxnovel.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://boxnovel.org/" target="_blank">https://boxnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/boxnovelorg.py" title="22 March 2022 02:50:32 PM">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://chrysanthemumgarden.com/" target="_blank">https://chrysanthemumgarden.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/c/chrysanthemumgarden.py" title="22 March 2022 02:50:32 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://clicknovel.net/" target="_blank">https://clicknovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/c/clicknovel.py" title="22 March 2022 02:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://comrademao.com/" target="_blank">https://comrademao.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/c/fu_kemao.py" title="22 March 2022 02:50:32 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://creativenovels.com/" target="_blank">https://creativenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/c/creativenovels.py" title="22 March 2022 02:50:32 PM">26</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/tidux"><img src="https://avatars.githubusercontent.com/u/1330562?v=4&s=24" alt="tidux" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://crescentmoon.blog/" target="_blank">https://crescentmoon.blog/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/c/crescentmoon.py" title="22 March 2022 02:50:32 PM">57</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://daonovel.com/" target="_blank">https://daonovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/daonovel.py" title="22 March 2022 02:50:32 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://demontranslations.com/" target="_blank">https://demontranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/demontrans.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dmtranslationscn.com/" target="_blank">https://dmtranslationscn.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/dmtrans.py" title="22 March 2022 02:50:32 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dobelyuwai.wordpress.com/" target="_blank">https://dobelyuwai.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/dobelyuwai.py" title="22 March 2022 02:50:32 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dragontea.ink/" target="_blank">https://dragontea.ink/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/dragon_tea.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dummynovels.com/" target="_blank">https://dummynovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/dummynovels.py" title="22 March 2022 03:03:29 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://exiledrebelsscanlations.com/" target="_blank">https://exiledrebelsscanlations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/e/exiledrebels.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://f-w-o.com/" target="_blank">https://f-w-o.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fantasyworldonline.py" title="22 March 2022 02:50:32 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fanstranslations.com/" target="_blank">https://fanstranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fanstrans.py" title="22 March 2022 02:50:32 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fujitranslation.com/" target="_blank">https://fujitranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fujitrans.py" title="22 March 2022 02:50:32 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hostednovel.com/" target="_blank">https://hostednovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/h/hostednovel.py" title="22 March 2022 02:50:32 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hui3r.wordpress.com/" target="_blank">https://hui3r.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/h/hui3r.py" title="22 March 2022 02:50:32 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://inadequatetranslations.wordpress.com/" target="_blank">https://inadequatetranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/i/inadequatetrans.py" title="22 March 2022 02:50:32 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://infinitenoveltranslations.net/" target="_blank">https://infinitenoveltranslations.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/i/infinitetrans.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://instadoses.com/" target="_blank">https://instadoses.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/i/instadoses.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://isotls.com/" target="_blank">https://isotls.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/i/isotls.py" title="22 March 2022 02:50:32 PM">56</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jpmtl.com/" target="_blank">https://jpmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/j/jpmtl.py" title="22 March 2022 02:50:32 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://justatranslatortranslations.com/" target="_blank">https://justatranslatortranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/j/justatrans.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://latestnovel.net/" target="_blank">https://latestnovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/latestnovel.py" title="22 March 2022 02:50:32 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/BorgSquared"><img src="https://avatars.githubusercontent.com/u/7807834?v=4&s=24" alt="BorgSquared" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lazybirdtranslations.wordpress.com/" target="_blank">https://lazybirdtranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/ladybirdtrans.py" title="22 March 2022 02:50:32 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lemontreetranslations.wordpress.com/" target="_blank">https://lemontreetranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lemontree.py" title="22 March 2022 02:50:32 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://light-novel.online/" target="_blank">https://light-novel.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelonline.py" title="22 March 2022 02:50:32 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovel.tv/" target="_blank">https://lightnovel.tv/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnoveltv.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovel.world/" target="_blank">https://lightnovel.world/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelworld.py" title="22 March 2022 02:50:32 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelbastion.com/" target="_blank">https://lightnovelbastion.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelbastion.py" title="22 March 2022 02:50:32 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelheaven.com/" target="_blank">https://lightnovelheaven.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelheaven.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelkiss.com/" target="_blank">https://lightnovelkiss.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelkiss.py" title="22 March 2022 02:50:32 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelreader.org/" target="_blank">https://lightnovelreader.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelreader.py" title="29 March 2022 04:52:29 AM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovels.me/" target="_blank">https://lightnovels.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelme.py" title="07 October 2021 04:35:06 PM">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelsonl.com/" target="_blank">https://lightnovelsonl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelsonl.py" title="22 March 2022 02:50:32 PM">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelstranslations.com/" target="_blank">https://lightnovelstranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovetrans.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/marcandjulien"><img src="https://avatars.githubusercontent.com/u/25230709?v=4&s=24" alt="marcandjulien" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://listnovel.com/" target="_blank">https://listnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/listnovel.py" title="22 March 2022 02:50:32 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login">🔑</span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lnmtl.com/" target="_blank">https://lnmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lnmtl.py" title="22 March 2022 02:50:32 PM">93</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lunarletters.com/" target="_blank">https://lunarletters.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lunarletters.py" title="22 March 2022 02:50:32 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.readlightnovel.cc/" target="_blank">https://m.readlightnovel.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readlightnovelcc.py" title="22 March 2022 02:50:32 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.webnovel.com/" target="_blank">https://m.webnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/webnovel.py" title="03 October 2021 10:34:45 AM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.wuxiaworld.co/" target="_blank">https://m.wuxiaworld.co/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaco.py" title="22 March 2022 02:56:57 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mangatoon.mobi/" target="_blank">https://mangatoon.mobi/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/mangatoon.py" title="22 March 2022 02:50:32 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://miraslation.net/" target="_blank">https://miraslation.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/miraslation.py" title="22 March 2022 02:50:32 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mtlreader.com/" target="_blank">https://mtlreader.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/mtlreader.py" title="18 November 2021 01:21:47 AM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://myboxnovel.com/" target="_blank">https://myboxnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/myboxnovel.py" title="22 March 2022 09:23:50 AM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mysticalmerries.com/" target="_blank">https://mysticalmerries.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/mysticalmerries.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novel27.com/" target="_blank">https://novel27.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novel27.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelcake.com/" target="_blank">https://novelcake.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelcake.py" title="22 March 2022 02:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfull.com/" target="_blank">https://novelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelfull.py" title="22 March 2022 02:50:32 PM">44</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfullplus.com/" target="_blank">https://novelfullplus.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelfullplus.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelgate.net/" target="_blank">https://novelgate.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelgate.py" title="22 March 2022 02:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelhi.com/" target="_blank">https://novelhi.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelhi.py" title="22 March 2022 02:50:32 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelmao.com/" target="_blank">https://novelmao.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelmao.py" title="22 March 2022 02:50:32 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://novelmic.com/" target="_blank">https://novelmic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelmic.py" title="22 March 2022 02:50:32 PM">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelonlinefree.com/" target="_blank">https://novelonlinefree.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelonlinefree.py" title="22 March 2022 02:50:32 PM">19</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelonlinefull.com/" target="_blank">https://novelonlinefull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelonlinefull.py" title="22 March 2022 02:50:32 PM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novels.pl/" target="_blank">https://novels.pl/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelspl.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsite.net/" target="_blank">https://novelsite.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelsite.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsonline.net/" target="_blank">https://novelsonline.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelsonline.py" title="22 March 2022 02:50:32 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsrock.com/" target="_blank">https://novelsrock.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelsrock.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltranslate.com/" target="_blank">https://noveltranslate.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/noveltranslate.py" title="20 September 2021 03:15:34 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltrench.com/" target="_blank">https://noveltrench.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/noveltrench.py" title="22 March 2022 02:50:32 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://omgnovels.com/" target="_blank">https://omgnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/o/omgnovels.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobes.net/" target="_blank">https://ranobes.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/ranobes.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readlightnovel.me/" target="_blank">https://readlightnovel.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readlightnovelorg.py" title="22 March 2022 02:50:32 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readlightnovels.net/" target="_blank">https://readlightnovels.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readlightnovelsnet.py" title="22 March 2022 02:50:32 PM">26</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readnovelfull.com/" target="_blank">https://readnovelfull.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readnovelfull.py" title="22 March 2022 02:50:32 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readwebnovels.net/" target="_blank">https://readwebnovels.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readwebnovels.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://reincarnationpalace.com/" target="_blank">https://reincarnationpalace.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/reincarnationpalace.py" title="22 March 2022 02:50:32 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rewayat.club/" target="_blank">https://rewayat.club/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/rewayatclub.py" title="22 March 2022 02:50:32 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rpgnoob.wordpress.com/" target="_blank">https://rpgnoob.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/rpgnovels.py" title="22 March 2022 02:50:32 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rpgnovels.com/" target="_blank">https://rpgnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/rpgnovels.py" title="22 March 2022 02:50:32 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://shalvationtranslations.wordpress.com/" target="_blank">https://shalvationtranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/shalvation.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://skynovel.org/" target="_blank">https://skynovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/skynovel.py" title="22 March 2022 02:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://sleepytranslations.com/" target="_blank">https://sleepytranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/sleepytrans.py" title="22 March 2022 02:50:32 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://smnovels.com/" target="_blank">https://smnovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/smnovels.py" title="22 March 2022 02:50:32 PM">59</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://steambunlightnovel.com/" target="_blank">https://steambunlightnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/steambun.py" title="28 March 2022 05:30:14 AM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://supernovel.net/" target="_blank">https://supernovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/supernovel.py" title="22 March 2022 02:50:32 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tipnovel.com/" target="_blank">https://tipnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/t/tipnovel.py" title="22 March 2022 02:50:32 PM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://toc.qidianunderground.org/" target="_blank">https://toc.qidianunderground.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/q/qidianunderground.py" title="12 August 2021 09:27:05 AM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/BorgSquared"><img src="https://avatars.githubusercontent.com/u/7807834?v=4&s=24" alt="BorgSquared" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tomotranslations.com/" target="_blank">https://tomotranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/t/tomotrans.py" title="22 March 2022 02:50:32 PM">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://totallytranslations.com/" target="_blank">https://totallytranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/t/totallytranslations.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://travistranslations.com/" target="_blank">https://travistranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/t/travistranslations.py" title="22 March 2022 02:50:32 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://vipnovel.com/" target="_blank">https://vipnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/v/vipnovel.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://vistranslations.wordpress.com/" target="_blank">https://vistranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/v/vistrans.py" title="22 March 2022 02:50:32 PM">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelonline.com/" target="_blank">https://webnovelonline.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/webnovelonlinecom.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelonline.net/" target="_blank">https://webnovelonline.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/webnovelonlinenet.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wnmtl.org/" target="_blank">https://wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wnmtl.py" title="22 March 2022 09:23:50 AM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wondernovels.com/" target="_blank">https://wondernovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wondernovels.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://woopread.com/" target="_blank">https://woopread.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/woopread.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/skyme5"><img src="https://avatars.githubusercontent.com/u/15525399?v=4&s=24" alt="skyme5" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wordexcerpt.com/" target="_blank">https://wordexcerpt.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wordexcerpt.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wordexcerpt.org/" target="_blank">https://wordexcerpt.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wordexcerpt.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wujizun.com/" target="_blank">https://wujizun.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wujizun.py" title="22 March 2022 02:56:57 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxia.city/" target="_blank">https://wuxia.city/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiacity.py" title="06 April 2022 02:56:19 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.io/" target="_blank">https://wuxiaworld.io/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaworldio.py" title="22 March 2022 02:56:57 PM">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.live/" target="_blank">https://wuxiaworld.live/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaworldlive.py" title="22 March 2022 02:56:57 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.name/" target="_blank">https://wuxiaworld.name/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaworldio.py" title="22 March 2022 02:56:57 PM">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.online/" target="_blank">https://wuxiaworld.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaonline.py" title="22 March 2022 02:50:32 PM">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworldsite.co/" target="_blank">https://wuxiaworldsite.co/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaworldsite.py" title="22 March 2022 02:50:32 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.allnovel.org/" target="_blank">https://www.allnovel.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/allnovel.py" title="22 March 2022 02:50:32 PM">38</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.asianhobbyist.com/" target="_blank">https://www.asianhobbyist.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/a/asianhobbyist.py" title="22 March 2022 02:50:32 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.box-novel.com/" target="_blank">https://www.box-novel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/b/boxnovelcom.py" title="22 March 2022 02:50:32 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.divinedaolibrary.com/" target="_blank">https://www.divinedaolibrary.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/d/divinedaolibrary.py" title="22 March 2022 02:50:32 PM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.f-w-o.com/" target="_blank">https://www.f-w-o.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fantasyworldonline.py" title="22 March 2022 02:50:32 PM">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fanfiction.net/" target="_blank">https://www.fanfiction.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fanfiction.py" title="22 March 2022 03:11:24 PM">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fictionpress.com/" target="_blank">https://www.fictionpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fictionpress.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.flying-lines.com/" target="_blank">https://www.flying-lines.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/flyinglines.py" title="06 April 2022 02:56:19 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.foxteller.com/" target="_blank">https://www.foxteller.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/foxteller.py" title="22 March 2022 02:50:32 PM">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.freelightnovel.com/" target="_blank">https://www.freelightnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/freelightnovel.py" title="22 March 2022 02:50:32 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fuyuneko.org/" target="_blank">https://www.fuyuneko.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/f/fuyuneko.py" title="22 March 2022 02:50:32 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.koreanmtl.online/" target="_blank">https://www.koreanmtl.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/k/koreanmtl.py" title="22 March 2022 02:50:32 PM">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelpub.com/" target="_blank">https://www.lightnovelpub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelpub.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelreader.org/" target="_blank">https://www.lightnovelreader.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelreader.py" title="29 March 2022 04:52:29 AM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelworld.com/" target="_blank">https://www.lightnovelworld.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/lightnovelpub.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ltnovel.com/" target="_blank">https://www.ltnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/l/ltnovel.py" title="22 March 2022 02:50:32 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.machine-translation.org/" target="_blank">https://www.machine-translation.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/machinetransorg.py" title="22 March 2022 02:50:32 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.miraslation.net/" target="_blank">https://www.miraslation.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/miraslation.py" title="22 March 2022 02:50:32 PM">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlreader.com/" target="_blank">https://www.mtlreader.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/m/mtlreader.py" title="18 November 2021 01:21:47 AM">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.neosekaitranslations.com/" target="_blank">https://www.neosekaitranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/neosekaitranslations.py" title="22 March 2022 02:50:32 PM">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelall.com/" target="_blank">https://www.novelall.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelall.py" title="28 March 2022 05:28:10 AM">59</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.novelcool.com/" target="_blank">https://www.novelcool.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelcool.py" title="22 March 2022 02:50:32 PM">28</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelhall.com/" target="_blank">https://www.novelhall.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelhall.py" title="22 March 2022 02:50:32 PM">57</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelhunters.com/" target="_blank">https://www.novelhunters.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelhunters.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmt.com/" target="_blank">https://www.novelmt.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelmt.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmtl.com/" target="_blank">https://www.novelmtl.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelmtl.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmultiverse.com/" target="_blank">https://www.novelmultiverse.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelmultiverse.py" title="22 March 2022 02:50:32 PM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelpassion.com/" target="_blank">https://www.novelpassion.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelpassion.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novels.pl/" target="_blank">https://www.novels.pl/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelspl.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelupdates.cc/" target="_blank">https://www.novelupdates.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/n/novelupdatescc.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.oppatranslations.com/" target="_blank">https://www.oppatranslations.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/o/oppatrans.py" title="22 March 2022 02:50:32 PM">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ornovel.com/" target="_blank">https://www.ornovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/o/ornovel.py" title="22 March 2022 02:50:32 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.cc/" target="_blank">https://www.readlightnovel.cc/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readlightnovelcc.py" title="22 March 2022 02:50:32 PM">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.me/" target="_blank">https://www.readlightnovel.me/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readlightnovelorg.py" title="22 March 2022 02:50:32 PM">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readwn.com/" target="_blank">https://www.readwn.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/readwn.py" title="22 March 2022 02:50:32 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.royalroad.com/" target="_blank">https://www.royalroad.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/r/royalroad.py" title="28 March 2022 05:24:55 AM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/Epicpkmn11"><img src="https://avatars.githubusercontent.com/u/41608708?v=4&s=24" alt="Epicpkmn11" height="24"/></a> <a href="https://github.com/aspin"><img src="https://avatars.githubusercontent.com/u/5728920?v=4&s=24" alt="aspin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.scribblehub.com/" target="_blank">https://www.scribblehub.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/scribblehub.py" title="22 March 2022 02:50:32 PM">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/Epicpkmn11"><img src="https://avatars.githubusercontent.com/u/41608708?v=4&s=24" alt="Epicpkmn11" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.shinsori.com/" target="_blank">https://www.shinsori.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/s/shinsori.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.tapread.com/" target="_blank">https://www.tapread.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/t/tapread.py" title="22 March 2022 02:50:32 PM">56</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.virlyce.com/" target="_blank">https://www.virlyce.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/v/virlyce.py" title="22 March 2022 02:50:32 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.volarenovels.com/" target="_blank">https://www.volarenovels.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/v/volarenovels.py" title="22 March 2022 02:50:32 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovel.com/" target="_blank">https://www.webnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/webnovel.py" title="03 October 2021 10:34:45 AM">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wnmtl.org/" target="_blank">https://www.wnmtl.org/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wnmtl.py" title="22 March 2022 09:23:50 AM">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxialeague.com/" target="_blank">https://www.wuxialeague.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxialeague.py" title="22 March 2022 02:50:32 PM">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiaworld.co/" target="_blank">https://www.wuxiaworld.co/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiaco.py" title="22 March 2022 02:56:57 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiaworld.com/" target="_blank">https://www.wuxiaworld.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/w/wuxiacom.py" title="04 February 2022 12:38:52 AM">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.xiainovel.com/" target="_blank">https://www.xiainovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/x/xiainovel.py" title="22 March 2022 02:50:32 PM">55</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://zinnovel.com/" target="_blank">https://zinnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/en/z/zinnovel.py" title="22 March 2022 02:50:32 PM">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
</tbody>
</table>


### `es` Spanish, Castilian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://cclawtranslations.home.blog/" target="_blank">https://cclawtranslations.home.blog/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/es/domentranslations.py" title="22 March 2022 02:50:32 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://domentranslations.wordpress.com/" target="_blank">https://domentranslations.wordpress.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/es/domentranslations.py" title="22 March 2022 02:50:32 PM">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
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
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/zhiend.py" title="22 March 2022 02:50:32 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zhi-end.blogspot.com/" target="_blank">http://zhi-end.blogspot.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/zhiend.py" title="22 March 2022 02:50:32 PM">61</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://darktranslation.com/" target="_blank">https://darktranslation.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/darktrans.py" title="22 March 2022 02:50:32 PM">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://grensia.blogspot.com/" target="_blank">https://grensia.blogspot.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/grensia_blogspot.py" title="22 March 2022 02:50:32 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://indowebnovel.id/" target="_blank">https://indowebnovel.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/indowebnovel.py" title="22 March 2022 02:50:32 PM">58</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://meionovel.id/" target="_blank">https://meionovel.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/meionovel.py" title="22 March 2022 02:50:32 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://morenovel.net/" target="_blank">https://morenovel.net/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/morenovel.py" title="22 March 2022 02:50:32 PM">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelgo.id/" target="_blank">https://novelgo.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/novelgo.py" title="22 March 2022 02:56:57 PM">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/AncientCatz"><img src="https://avatars.githubusercontent.com/u/69200720?v=4&s=24" alt="AncientCatz" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelringan.com/" target="_blank">https://novelringan.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/novelringan.py" title="22 March 2022 02:50:32 PM">57</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltoon.mobi/" target="_blank">https://noveltoon.mobi/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/noveltoon.py" title="22 March 2022 02:56:57 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wbnovel.com/" target="_blank">https://wbnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/wbnovel.py" title="22 March 2022 02:50:32 PM">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelindonesia.com/" target="_blank">https://webnovelindonesia.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/webnovelindonesia.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.idqidian.us/" target="_blank">https://www.idqidian.us/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/idqidian.py" title="22 March 2022 02:50:32 PM">43</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovelover.com/" target="_blank">https://www.webnovelover.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/webnovelover.py" title="22 March 2022 02:50:32 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.worldnovel.online/" target="_blank">https://www.worldnovel.online/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/worldnovelonline.py" title="22 March 2022 02:50:32 PM">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://yukinovel.id/" target="_blank">https://yukinovel.id/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/id/yukinovel.py" title="22 March 2022 02:50:32 PM">54</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
</tbody>
</table>


### `multi` Multilingual

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://es.mtlnovel.com/" target="_blank">http://es.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://fr.mtlnovel.com/" target="_blank">http://fr.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://id.mtlnovel.com/" target="_blank">http://id.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.mtlnovel.com/" target="_blank">http://www.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://18.foxaholic.com/" target="_blank">https://18.foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/foxaholic.py" title="22 March 2022 02:50:32 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://es.mtlnovel.com/" target="_blank">https://es.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://foxaholic.com/" target="_blank">https://foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/foxaholic.py" title="22 March 2022 02:50:32 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fr.mtlnovel.com/" target="_blank">https://fr.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://global.foxaholic.com/" target="_blank">https://global.foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/foxaholic.py" title="22 March 2022 02:50:32 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://id.mtlnovel.com/" target="_blank">https://id.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://my.w.tt/" target="_blank">https://my.w.tt/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/wattpad.py" title="06 April 2022 02:56:19 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.foxaholic.com/" target="_blank">https://www.foxaholic.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/foxaholic.py" title="22 March 2022 02:50:32 PM">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/frybin"><img src="https://avatars.githubusercontent.com/u/17693407?v=4&s=24" alt="frybin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlnovel.com/" target="_blank">https://www.mtlnovel.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py" title="22 March 2022 02:50:32 PM">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wattpad.com/" target="_blank">https://www.wattpad.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/wattpad.py" title="06 April 2022 02:56:19 PM">64</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
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
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://litnet.com/" target="_blank">https://litnet.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/ru/litnet.py" title="22 March 2022 02:50:32 PM">3</a></td>
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
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/vi/lnhakone.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ln.hako.re/" target="_blank">https://ln.hako.re/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/vi/lnhakone.py" title="22 March 2022 02:50:32 PM">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://truyenfull.vn/" target="_blank">https://truyenfull.vn/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/vi/truenfull.py" title="22 March 2022 02:50:32 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://truyentr.info/" target="_blank">https://truyentr.info/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/vi/truenfull.py" title="22 March 2022 02:50:32 PM">3</a></td>
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
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://book.qidian.com/" target="_blank">https://book.qidian.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/zh/qidiancom.py" title="22 March 2022 02:50:32 PM">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tw.m.ixdzs.com/" target="_blank">https://tw.m.ixdzs.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/zh/ixdzs.py" title="22 March 2022 02:50:32 PM">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/junqili259"><img src="https://avatars.githubusercontent.com/u/39481617?v=4&s=24" alt="junqili259" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.aixdzs.com/" target="_blank">https://www.aixdzs.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/zh/aixdzs.py" title="22 March 2022 02:50:32 PM">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.daocaorenshuwu.com/" target="_blank">https://www.daocaorenshuwu.com/</a></td>
<td><a href="https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/zh/daocaorenshuwu.py" title="22 March 2022 02:50:32 PM">56</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
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
<tr><td><a href="http://boxnovel.cloud/" target="_blank">http://boxnovel.cloud/</a></td>
<td>This domain has expired</td>
</tr>
<tr><td><a href="http://fastnovel.net/" target="_blank">http://fastnovel.net/</a></td>
<td>Access denied</td>
</tr>
<tr><td><a href="http://fullnovel.live/" target="_blank">http://fullnovel.live/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="http://gravitytales.com/" target="_blank">http://gravitytales.com/</a></td>
<td>Domain is expired</td>
</tr>
<tr><td><a href="http://novels.cloud/" target="_blank">http://novels.cloud/</a></td>
<td>This domain has expired</td>
</tr>
<tr><td><a href="http://tiknovel.com/" target="_blank">http://tiknovel.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="http://wuxiaworld.cloud/" target="_blank">http://wuxiaworld.cloud/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="http://www.hanyunovels.site/" target="_blank">http://www.hanyunovels.site/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="http://www.indonovels.net/" target="_blank">http://www.indonovels.net/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="http://www.machinenoveltranslation.com/" target="_blank">http://www.machinenoveltranslation.com/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="http://www.tiknovel.com/" target="_blank">http://www.tiknovel.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://4scanlation.com/" target="_blank">https://4scanlation.com/</a></td>
<td>Domain expired</td>
</tr>
<tr><td><a href="https://9kqw.com/" target="_blank">https://9kqw.com/</a></td>
<td>This domain has expired</td>
</tr>
<tr><td><a href="https://anonanemone.wordpress.com/" target="_blank">https://anonanemone.wordpress.com/</a></td>
<td>No longer available</td>
</tr>
<tr><td><a href="https://anythingnovel.com/" target="_blank">https://anythingnovel.com/</a></td>
<td>The domain is for sale</td>
</tr>
<tr><td><a href="https://bestoflightnovels.com/" target="_blank">https://bestoflightnovels.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://boxnovel.online/" target="_blank">https://boxnovel.online/</a></td>
<td>Redirects to tipnovel.com</td>
</tr>
<tr><td><a href="https://dsrealmtranslations.com/" target="_blank">https://dsrealmtranslations.com/</a></td>
<td>No longer serves lightnovels</td>
</tr>
<tr><td><a href="https://fsapk.com/" target="_blank">https://fsapk.com/</a></td>
<td>Site is not working</td>
</tr>
<tr><td><a href="https://indomtl.com/" target="_blank">https://indomtl.com/</a></td>
<td>Not crawler friendly</td>
</tr>
<tr><td><a href="https://indonovels.blogspot.co.id/" target="_blank">https://indonovels.blogspot.co.id/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://kiss-novel.com/" target="_blank">https://kiss-novel.com/</a></td>
<td>Redirects to wuxiaworldsite.co</td>
</tr>
<tr><td><a href="https://lightnovelshub.com/" target="_blank">https://lightnovelshub.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://m.1ksy.com/" target="_blank">https://m.1ksy.com/</a></td>
<td>Web server is down</td>
</tr>
<tr><td><a href="https://m.chinesefantasynovels.com/" target="_blank">https://m.chinesefantasynovels.com/</a></td>
<td>Connection timed out</td>
</tr>
<tr><td><a href="https://m.mywuxiaworld.com/" target="_blank">https://m.mywuxiaworld.com/</a></td>
<td>Web server is returning an unknown error</td>
</tr>
<tr><td><a href="https://m.romanticlovebooks.com/" target="_blank">https://m.romanticlovebooks.com/</a></td>
<td>Web server is down</td>
</tr>
<tr><td><a href="https://moonstonetranslation.com/" target="_blank">https://moonstonetranslation.com/</a></td>
<td>This site can not be reached</td>
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
<tr><td><a href="https://novelextra.com/" target="_blank">https://novelextra.com/</a></td>
<td>Invalid SSL certificate</td>
</tr>
<tr><td><a href="https://novelplanet.com/" target="_blank">https://novelplanet.com/</a></td>
<td>Site is closed</td>
</tr>
<tr><td><a href="https://novelraw.blogspot.com/" target="_blank">https://novelraw.blogspot.com/</a></td>
<td>Site closed down</td>
</tr>
<tr><td><a href="https://overabook.com/" target="_blank">https://overabook.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://pery.info/" target="_blank">https://pery.info/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://ranobelib.me/" target="_blank">https://ranobelib.me/</a></td>
<td>Access denied</td>
</tr>
<tr><td><a href="https://readnovelz.net/" target="_blank">https://readnovelz.net/</a></td>
<td>Redirects to webnovelonline.net</td>
</tr>
<tr><td><a href="https://tiknovel.com/" target="_blank">https://tiknovel.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://tunovelaligera.com/" target="_blank">https://tunovelaligera.com/</a></td>
<td>Broken. Chapters does not load</td>
</tr>
<tr><td><a href="https://viewnovel.net/" target="_blank">https://viewnovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://webnovel.online/" target="_blank">https://webnovel.online/</a></td>
<td>The site has no content</td>
</tr>
<tr><td><a href="https://writerupdates.com/" target="_blank">https://writerupdates.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://wuxiaworld.site/" target="_blank">https://wuxiaworld.site/</a></td>
<td>Access denied</td>
</tr>
<tr><td><a href="https://www.1ksy.com/" target="_blank">https://www.1ksy.com/</a></td>
<td>Web server is down</td>
</tr>
<tr><td><a href="https://www.anonanemone.wordpress.com/" target="_blank">https://www.anonanemone.wordpress.com/</a></td>
<td>No longer available</td>
</tr>
<tr><td><a href="https://www.centinni.com/" target="_blank">https://www.centinni.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.mywuxiaworld.com/" target="_blank">https://www.mywuxiaworld.com/</a></td>
<td>Web server is returning an unknown error</td>
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
<tr><td><a href="https://www.romanticlovebooks.com/" target="_blank">https://www.romanticlovebooks.com/</a></td>
<td>Web server is down</td>
</tr>
<tr><td><a href="https://www.tiknovel.com/" target="_blank">https://www.tiknovel.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://www.translateindo.com/" target="_blank">https://www.translateindo.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.x81zw.com/" target="_blank">https://www.x81zw.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://www.xsbiquge.com/" target="_blank">https://www.xsbiquge.com/</a></td>
<td>Redirects to https://www.biqufan.com/</td>
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
