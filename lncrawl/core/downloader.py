# -*- coding: utf-8 -*-
"""
To download chapter bodies
"""
import base64
import hashlib
import json
import logging
import os
from io import BytesIO
import signal

import bs4
from PIL import Image
from tqdm import tqdm

from ..core.exeptions import LNException
from .arguments import get_args

logger = logging.getLogger(__name__)

def resolve_all_futures(futures_to_check, desc='', unit=''):
    if not futures_to_check:
        return
    # end if
    is_debug_mode = os.getenv('debug_mode') == 'yes'
    bar = tqdm(desc=desc, unit=unit,
               total=len(futures_to_check), 
               disable=is_debug_mode)
    
    def cancel_all(*args):
        bar.close()
        for future in futures_to_check:
            if not future.done():
                future.cancel()
            # end if
        # end for
        if len(args):
            raise LNException('Cancelled by user')
        # end if
    # end def

    signal.signal(signal.SIGINT, cancel_all)

    try:
        for future in futures_to_check:
            try:
                message = future.result()
                if message and not is_debug_mode:
                    bar.clear()
                    logger.warning(message)
                # end if
            finally:
                bar.update()
            # end try
        # end for
    finally:
        cancel_all()
    # end try
# end def

def get_chapter_filename(app, chapter):
    from .app import App
    assert isinstance(app, App)

    dir_name = os.path.join(app.output_path, 'json')
    if app.pack_by_volume:
        vol_name = 'Volume ' + str(chapter['volume']).rjust(2, '0')
        dir_name = os.path.join(dir_name, vol_name)
    # end if

    chapter_name = str(chapter['id']).rjust(5, '0')
    return os.path.join(dir_name, chapter_name + '.json')
# end def


def extract_chapter_images(app, chapter):
    from .app import App
    assert isinstance(app, App)
    assert app.crawler is not None
    assert isinstance(chapter, dict), 'Invalid chapter'

    if not chapter['body']:
        return
    # end if 

    chapter.setdefault('images', {})
    soup = app.crawler.make_soup(chapter['body'])
    for img in soup.select('img'):
        if not img or not img.has_attr('src'):
            continue
        # end if
        full_url = app.crawler.absolute_url(img['src'], page_url=chapter['url'])   
        filename = hashlib.md5(full_url.encode()).hexdigest() + '.jpg'
        img.attrs = {'src': 'images/' + filename, 'alt': filename}
        chapter['images'][filename] = full_url
    # end for
    
    soup_body = soup.select_one('body')
    assert isinstance(soup_body, bs4.Tag), 'Invalid soup body'
    chapter['body'] = ''.join([str(x) for x in soup_body.contents])
# end def


def save_chapter_body(app, chapter):
    from .app import App
    assert isinstance(app, App)

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


def download_chapter_body(app, chapter):
    assert isinstance(chapter, dict)
    from .app import App
    assert isinstance(app, App)
    assert app.crawler is not None

    try:
        # Check previously downloaded chapter
        file_name = get_chapter_filename(app, chapter)
        if os.path.exists(file_name):
            logger.debug('Restoring from %s', file_name)
            with open(file_name, 'r', encoding="utf-8") as file:
                old_chapter = json.load(file)
            # end with
            chapter.update(**old_chapter)
        # end def
        
        if chapter.get('body') and chapter.get('success'):
            return
        # end if

        # Fetch chapter body if it does not exists
        logger.debug('Downloading chapter %d: %s', chapter['id'], chapter['url'])
        chapter['body'] = app.crawler.download_chapter_body(chapter)
        extract_chapter_images(app, chapter)
        chapter['success'] = True
    except KeyboardInterrupt:
        raise LNException('Chapter download cancelled by user')
    except Exception as e:
        logger.debug('Failed', e)
        return f"[{chapter['id']}] Failed to get chapter body ({e.__class__.__name__}: {e})"
    finally:
        chapter.setdefault('body', '')
        save_chapter_body(app, chapter)
        app.progress += 1
    # end try
# end def


def download_chapters(app):
    from .app import App
    assert isinstance(app, App)
    assert app.crawler is not None

    if not app.output_formats:
        app.output_formats = {}
    # end if

    app.progress = 0
    futures_to_check = [
        app.crawler.executor.submit(
            download_chapter_body,
            app,
            chapter,
        )
        for chapter in app.chapters
    ]

    try:
        resolve_all_futures(futures_to_check, desc='Chapters', unit='item')
    finally:
        logger.info('Processed %d chapters' % app.progress)
    # end try
# end def


def download_image(app, url) -> Image.Image:
    from .app import App
    assert isinstance(app, App)
    assert app.crawler is not None

    assert isinstance(url, str), 'Invalid image url'
    if len(url) > 1000 or url.startswith('data:'):
        content = base64.b64decode(url.split('base64,')[-1])
    else:
        content = app.crawler.download_image(url)
    # end if
    return Image.open(BytesIO(content))
# end def


def download_cover_image(app):
    from .app import App
    assert isinstance(app, App)
    assert app.crawler is not None

    filename = os.path.join(app.output_path, 'cover.jpg')

    if not os.path.isfile(filename):
        cover_urls = [
            app.crawler.novel_cover,
            'https://source.unsplash.com/featured/800x1032?abstract',
        ]
        for url in cover_urls:
            try:
                logger.info('Downloading cover image: %s', url)
                img = download_image(app, url)
                img.convert('RGB').save(filename, "JPEG")
                logger.debug('Saved cover: %s', filename)
                app.progress += 1
                break
            except KeyboardInterrupt as e:
                raise LNException('Cover download cancelled by user')
            except Exception as e:
                logger.debug('Failed to get cover: %s', url, e)
            # end try
        # end for
    # end if
             
    if not os.path.isfile(filename):
        return f"[{filename}] Failed to download cover image"
    # end if
    
    app.crawler.novel_cover = filename
    app.book_cover = filename
# end def


def download_content_image(app, url, filename):
    from .app import App
    assert isinstance(app, App)
    image_folder = os.path.join(app.output_path, 'images')
    image_file = os.path.join(image_folder, filename)
    try:
        if os.path.isfile(image_file):
            return
        # end if
        img = download_image(app, url)        
        os.makedirs(image_folder, exist_ok=True)
        with open(image_file, 'wb') as f:
            img.convert('RGB').save(f, "JPEG")
            logger.debug('Saved image: %s', image_file)
        # end with
    except KeyboardInterrupt as e:
        raise LNException('Image download cancelled by user')
    except Exception as e:
        return f"[{filename}] Failed to get content image: {url} | {e.__class__.__name__}: {e}"
    finally:
        app.progress += 1
    # end try
# end def


def download_chapter_images(app):
    from .app import App
    assert isinstance(app, App)
    assert app.crawler is not None

    # download or generate cover
    app.progress = 0
    futures_to_check = [
        app.crawler.executor.submit(
            download_cover_image,
            app,
        )
    ]
    futures_to_check += [
        app.crawler.executor.submit(
            download_content_image,
            app,
            url,
            filename,
        )
        for chapter in app.chapters
        for filename, url in chapter.get('images', {}).items()
    ]

    try:
        resolve_all_futures(futures_to_check, desc='  Images', unit='item')
    finally:
        logger.info('Processed %d images' % app.progress)
    # end try
# end def
