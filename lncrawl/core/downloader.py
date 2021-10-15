# -*- coding: utf-8 -*-
"""
To download chapter bodies
"""
import base64
import hashlib
import json
import logging
import os
import time
from io import BytesIO

from PIL import Image
from tqdm import tqdm

from .arguments import get_args

logger = logging.getLogger(__name__)

def download_image(app, url) -> Image.Image:
    '''Download image'''
    assert isinstance(url, str)
    if len(url) > 1000 or url.startswith('data:'):
        content = base64.b64decode(url.split('base64,')[-1])
    else:
        content = app.crawler.download_image(url)
    # end if
    return Image.open(BytesIO(content))
# end def

def download_cover(app):
    filename = None
    filename = os.path.join(app.output_path, 'cover.jpg')
    if os.path.exists(filename):
        return filename

    logger.info('Downloading original cover image...')
    image_url = app.crawler.novel_cover
    try:
        img = download_image(app, image_url)
        img.convert('RGB').save(filename, "JPEG")
        logger.debug('Saved cover: %s', filename)
        return filename
    except Exception as ex:
        logger.warn('Failed to download original cover image: %s -> %s (%s)',
                    image_url, filename, str(ex))
    # end try

    logger.info('Downloading fallback cover image...')
    image_url = 'https://source.unsplash.com/featured/800x1032?abstract'
    try:
        img = download_image(app, image_url)
        img.convert('RGB').save(filename, "JPEG")
        logger.debug('Saved cover: %s', filename)
        return filename
    except Exception as ex:
        logger.warn('Failed to download fallback cover image: %s -> %s (%s)',
                    image_url, filename, str(ex))
    # end try
    return None
# end def


def download_chapter_body(app, chapter):
    result = None
    chapter['body'] = read_chapter_body(app, chapter)

    if not chapter['body']:
        retry_count = 3
        chapter['body'] = ''
        for i in range(retry_count):
            try:
                logger.debug('Downloading chapter %d: %s', chapter['id'], chapter['url'])
                chapter['body'] = app.crawler.download_chapter_body(chapter)
                break
            except Exception as e:
                if i == retry_count:
                    logger.exception('Failed to download chapter body')
                else:
                    logger.debug('Error: %s. Retrying...', str(e))
                    time.sleep(3 + 5 * i)  # wait before next retry
                # end if
            # end try
        # end for
    # end if

    if not chapter['body']:
        result = 'Body is empty: ' + chapter['url']
    else:
        save_chapter_body(app, chapter)
    # end if

    app.progress += 1
    return result
# end def


def get_chapter_filename(app, chapter):
    dir_name = os.path.join(app.output_path, 'json')
    if app.pack_by_volume:
        vol_name = 'Volume ' + str(chapter['volume']).rjust(2, '0')
        dir_name = os.path.join(dir_name, vol_name)
    # end if

    chapter_name = str(chapter['id']).rjust(5, '0')
    return os.path.join(dir_name, chapter_name + '.json')
# end def


def read_chapter_body(app, chapter):
    file_name = get_chapter_filename(app, chapter)

    chapter['body'] = ''
    if os.path.exists(file_name):
        logger.debug('Restoring from %s', file_name)
        with open(file_name, 'r', encoding="utf-8") as file:
            old_chapter = json.load(file)
            chapter['body'] = old_chapter['body']
        # end with
    # end if

    return chapter['body']
# end def


def save_chapter_body(app, chapter):
    file_name = get_chapter_filename(app, chapter)

    title = chapter['title'].replace('>', '&gt;').replace('<', '&lt;')
    if title not in chapter['body']:
        chapter['body'] = '<h1>%s</h1>\n%s' % (title, chapter['body'])
    if get_args().add_source_url and chapter['url'] not in chapter['body']:
        chapter['body'] += '<br><p>Source: <a href="%s">%s</a></p>' % (
            chapter['url'], chapter['url'])
    # end if

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(json.dumps(chapter, ensure_ascii=False))
    # end with
# end def


def download_content_image(app, url, filename):
    image_folder = os.path.join(app.output_path, 'images')
    image_file = os.path.join(image_folder, filename)
    try:
        if os.path.isfile(image_file):
            return filename
        # end if

        img = download_image(app, url)
        os.makedirs(image_folder, exist_ok=True)
        with open(image_file, 'wb') as f:
            img.convert('RGB').save(f, "JPEG")
            logger.debug('Saved image: %s', image_file)
        # end with
        return filename
    except Exception as ex:
        logger.debug('Failed to download image: %s (%s)', image_file, str(ex))
        return None
    finally:
        app.progress += 1
    # end try
# end def

def download_chapters(app):
    app.progress = 0
    bar = tqdm(desc='Downloading', total=len(app.chapters), unit='ch')
    if os.getenv('debug_mode') == 'yes':
        bar.update = lambda n=1: None  # Hide in debug mode
    # end if
    bar.clear()

    if not app.output_formats:
        app.output_formats = {}
    # end if

    futures_to_check = [
        app.crawler.executor.submit(
            download_chapter_body,
            app,
            chapter,
        )
        for chapter in app.chapters
    ]

    for future in futures_to_check:
        result = future.result()
        if result:
            bar.clear()
            logger.error(result)
        # end if
        bar.update()
    # end for

    bar.close()
    print('Processed %d chapters' % len(app.chapters))
# end def


def download_chapter_images(app):
    app.progress = 0

    # download or generate cover
    app.book_cover = download_cover(app)
    if not app.book_cover:
        logger.warn('No cover image')
    # end if

    image_count = 0
    futures_to_check = {}
    for chapter in app.chapters:
        if not chapter.get('body'):
            continue
        # end if

        soup = app.crawler.make_soup(chapter['body'])
        for img in soup.select('img'):
            full_url = app.crawler.absolute_url(img['src'], page_url=chapter['url'])
            filename = hashlib.md5(img['src'].encode()).hexdigest() + '.jpg'
            future = app.crawler.executor.submit(download_content_image, app, full_url, filename)
            futures_to_check.setdefault(chapter['id'], [])
            futures_to_check[chapter['id']].append(future)
            image_count += 1
        # end for
    # end for

    if image_count == 0:
        return
    # end if

    bar = tqdm(desc='Images', total=image_count, unit='img')
    if os.getenv('debug_mode') == 'yes':
        bar.update = lambda n=1: None  # Hide in debug mode
    # end if
    bar.clear()

    for chapter in app.chapters:
        if chapter['id'] not in futures_to_check:
            continue
        # end if

        images = []
        for future in futures_to_check[chapter['id']]:
            images.append(future.result())
            bar.update()
        # end for
        logger.debug(images)

        soup = app.crawler.make_soup(chapter['body'])
        for img in soup.select('img'):
            filename = hashlib.md5(img['src'].encode()).hexdigest() + '.jpg'
            if filename in images:
                img.attrs = {'src': 'images/%s' % filename, 'alt': filename}
                # img['style'] = 'float: left; margin: 15px; width: 100%;'
            else:
                img.extract()
            # end if
        # end for

        chapter['body'] = ''.join([str(x) for x in soup.select_one('body').contents])
        save_chapter_body(app, chapter)
    # end for

    bar.close()
    print('Processed %d images' % image_count)
# end def
