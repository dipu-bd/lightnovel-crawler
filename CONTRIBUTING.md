# The Project Structure

## Initialize

- The `lncrawl` is the source folder.
- The file `lncrawl/__init__.py` loads `.env` if exists and calls `lncrawl/core/__init__.py`. This files loads basic settings and checks the latest version.
- Next, it calls `bots/__init__.py` to start the selected bot. By default it calls the `console` bot. Otherwise, the bot specified in `.env` file will be called.
- Every bot uses an instance of `App` class from `core/app.py` to handle user request.

## Introducing core files

- The `core/arguments.py` uses `ArgumentParser` from `argparse` and ensures that the arguments passed to the app is valid.
- `core/app.py` contains class `App`. It has all necessary methods to process user requests. It creates new crawlers, do the crawling, and generate output files. The bots should use this to process user input.
  - When user provides an input, call `init_search` method. First it checks whether the input is an url, or a search query.
  - If it is an URL, it is matched againsts `crawler_list` from `spiders/__init__.py`. If a match found the input url is passed to `init_crawler` method.
  - Otherwise, It will call the `search_novel` defined in crawler instances. Find out which of the search result is the desired novel by user and call `init_crawler` method.
  - The `init_crawler` will create and initialize a crawler instance using the given url.
  - Next, the `get_novel_info` gets called to retrieve the novel page info, like- title, author, cover, volumes and chapters.
  - After setting the list of chapters to download in `chapters` field, bots calls `start_download`.
  - When download finishes, it calls `bind_books`. The chat bots may use `compress_output` to compress output files into a single `zip` archive.
- The `core/novel_info.py` process the crawled novel page, like- volume list, chapter list etc.
- The `core/downloader.py` is to download chapter list using `ThreadPoolExecutor` created by default using `5` max-workers inside `utils/crawler.py`.

## Introducing spiders

- Crawlers are inside `spiders` folder.
- The `spiders/__init__.py` is very important. It has `crawler_list` variable, which maps the crawler class definition to url of the source.
- You must use `spiders/_sample.py` as template and extend `utils/crawler.py`. It contains a lot of helpers.
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
