# LightNovels To EBook

Crawls lightnovels from popular websites and converts to ebook format (only EPUB and MOBI are supported for now).

## Tutorial

### Installation

To use this app, you need to have python3 installed in your computer. You can install the package using either of the following methods:

- Using pip:

```bash
$ pip install ebook-crawler
# Or,
$ python3 -m pip install --user ebook-crawler
```

- Using `setup.py`:

```bash
$ wget https://github.com/dipu-bd/site-to-epub/releases/download/v1.2/ebook_crawler-1.2.tar.gz
$ tar -xvzf ebook_crawler-1.2.tar.gz
$ cd ebook_crawler-1.2
$ python3 setup.py install
```

### Test it out:

**Open the console panel in a directory you want to download novels**. Your current directory is used to store downloaded data.

```
$ ebook_crawler

EbookCrawler:
  python . <site-handle> <novel-id> [<start-chapter>|<start-url>] [<end-chapter>|<end-url>]
.
.
.
```

### Parameters to pass

#### 1. Site Handle (required)

The avaiable list of site handles are given below. *To request new site [create a new issues](https://github.com/dipu-bd/site-to-epub/issues) requesting it*.

| Handle | Website |
|--------|---------|
| `webnovel` | https://www.webnovel.com |
| `wuxia` | http://www.wuxiaworld.com |
| `lnmtl` | https://lnmtl.com |
| `readln` | https://www.readlightnovel.org |

#### 2. Novel ID (required)

To download a novel, you need to get a `novel-id`. It is usually a unique part of the url that gives you the profile page of a novel. Following table shows some examples of `novel-id`:

| URL | Novel ID |
|-----|----------|
| https://www.webnovel.com/book/8143258106003605 | 8143258106003605 |
| https://lnmtl.com/novel/against-the-gods | against-the-gods |
| https://www.readlightnovel.org/tales-of-herding-gods | tales-of-herding-gods |
| http://www.wuxiaworld.com/novel/desolate-era | desolate-era |

#### 3. Start Chapter or Start URL (optional)

You can provide either a chapter number or the url of a chapter (see examples below). Chapter number is usually the index of the chapter in the chapter list that is given in the website. (except for LNMLT, see below).

> for LNMTL, the chapter number should be the serial number of a chapter. Some novels has extra chapters and OVAs. In that case, *the serial number might not match with the real chapter number*.

If you are not sure about the chapter number, just provide an url to the chapter page.

**NOTE:** *if you do not provide this field, but has already downloaded data, they will be used to bind ebooks.*

> HINT: Pass `1` to start the download from the beginning.

Example values:

- https://www.webnovel.com/book/8143258106003605/21860374051617214
- https://www.wuxiaworld.com/novel/a-will-eternal/awe-chapter-1
- https://lnmtl.com/chapter/against-the-gods-book-11-chapter-1135
- https://www.readlightnovel.org/tales-of-herding-gods

<!-- - KindleComicConverter: `pip install -U KindleComicConverter` -->

#### 4. End Chapter or End URL (optional)

Same rules described for the start chapters applies here. You can choose not to give an end chapter. But you have to provide an end-chapter greater than the start-chapter.

**NOTE:** *If you do not provide this field, the novel will be crawled from the start chapter until the end.*


#### Finally, some warnings...

- Do not use too many instances of this program too frequently. Otherwise it might cause traffic jam to your favorite website. We do not want others to suffer for our sake, right?

- Do not download too frequently from LNTML. They blocks your IP if too many consecutives requests is observed.

- This program has the capability to perform DDOS attacks that can cause a website to go down. Like a good netizen, make a promise you will do no such things!

## External Resources

- KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211

