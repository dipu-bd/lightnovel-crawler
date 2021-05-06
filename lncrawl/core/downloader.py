# -*- coding: utf-8 -*-
"""
To download chapter bodies
"""
import hashlib
import json
import logging
import os
import time
from io import BytesIO

from PIL import Image
from progress.bar import IncrementalBar

from ..core.arguments import get_args

logger = logging.getLogger(__name__)

try:
    from ..utils.racovimge import random_cover
except ImportError as err:
    logger.debug(err)

try:
    from cairosvg import svg2png
except Exception:
    svg2png = None
    logger.info('CairoSVG was not found.' +
                'Install it to generate random cover image:\n' +
                '    pip install cairosvg')
# end try


def download_cover(app):
    if not app.crawler.novel_cover:
        return None
    # end if

    filename = None
    try:
        filename = os.path.join(app.output_path, 'cover.png')
        if os.path.exists(filename):
            return filename
        # end if
    except Exception as ex:
        logger.warn('Failed to locate cover image: %s -> %s (%s)',
                    app.crawler.novel_cover, app.output_path, str(ex))
        return None
    # end try

    try:
        logger.info('Downloading cover image...')
        response = app.crawler.get_response(app.crawler.novel_cover)
        img = Image.open(BytesIO(response.content))
        img.save(filename)
        logger.debug('Saved cover: %s', filename)
        return filename
    except Exception as ex:
        logger.warn('Failed to download cover image: %s -> %s (%s)',
                    app.crawler.novel_cover, filename, str(ex))
        return None
    # end try
# end def


def generate_cover(app):
    logger.info('Generating cover image...')
    if svg2png is None:
        return
    # end if
    try:
        svg_file = os.path.join(app.output_path, 'cover.svg')
        svg = random_cover(
            title=app.crawler.novel_title,
            author=app.crawler.novel_author,
        )

        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(svg)
            logger.debug('Saved a random cover.svg')
        # end with

        png_file = os.path.join(app.output_path, 'cover.png')
        svg2png(bytestring=svg.encode('utf-8'), write_to=png_file)
        logger.debug('Converted cover.svg to cover.png')

        return png_file
    except Exception:
        logger.exception('Failed to generate cover image: %s', app.output_path)
        return None
    # end try
# end def


def download_chapter_body(app, chapter):
    result = None

    dir_name = os.path.join(app.output_path, 'json')
    if app.pack_by_volume:
        vol_name = 'Volume ' + str(chapter['volume']).rjust(2, '0')
        dir_name = os.path.join(dir_name, vol_name)
    # end if

    chapter_name = str(chapter['id']).rjust(5, '0')
    file_name = os.path.join(dir_name, chapter_name + '.json')

    chapter['body'] = ''
    if os.path.exists(file_name):
        logger.debug('Restoring from %s', file_name)
        with open(file_name, 'r', encoding="utf-8") as file:
            old_chapter = json.load(file)
            chapter['body'] = old_chapter['body']
        # end with
    # end if

    if len(chapter['body']) == 0:
        body = ''
        retry_count = 2
        for i in range(retry_count + 1):
            try:
                logger.debug('Downloading to %s', file_name)
                body = app.crawler.download_chapter_body(chapter)
                break
            except Exception:
                if i == retry_count:
                    logger.exception('Failed to download chapter body')
                else:
                    time.sleep(1 + 5 * i)  # wait before next retry
                # end if
            # end try
        # end for
        if not body:
            result = 'Body is empty: ' + chapter['url']
        else:
            if not('body_lock' in chapter and chapter['body_lock']):
                body = app.crawler.cleanup_text(body)
            # end if
            title = chapter['title'].replace('>', '&gt;').replace('<', '&lt;')
            chapter['body'] = '<h1>%s</h1>\n%s' % (title, body)
            if get_args().add_source_url:
                chapter['body'] += '<br><p>Source: <a href="%s">%s</a></p>' % (
                    chapter['url'], chapter['url'])
            # end if
        # end if

        os.makedirs(dir_name, exist_ok=True)
        with open(file_name, 'w', encoding="utf-8") as file:
            file.write(json.dumps(chapter))
        # end with
    # end if

    app.progress += 1
    return result
# end def


def download_image(app, url, image_output_path):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    filename = url_hash + '.jpg'
    image_file = os.path.join(image_output_path, filename)
    if os.path.isfile(image_file):
        app.progress += 1
        return (url, filename)
    # end if

    try:
        logger.info('Downloading image: ' + url)
        response = app.crawler.get_response(url)
        img = Image.open(BytesIO(response.content))
        os.makedirs(image_output_path, exist_ok=True)
        with open(image_file, 'wb') as f:
            img.save(f, "JPEG")
            logger.debug('Saved image: %s', image_file)
        # end with
        return (url, filename)
    except Exception as ex:
        logger.debug('Failed to download image: %s -> %s (%s)', url, filename, str(ex))
        return (url, None)
    finally:
        app.progress += 1
    # end try
# end def


def download_chapters(app):
    app.progress = 0
    bar = IncrementalBar('Downloading chapters', max=len(app.chapters))
    if os.getenv('debug_mode') == 'yes':
        bar.next = lambda: None  # Hide in debug mode
        bar.finish()
    else:
        bar.start()
    # end if

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
            bar.clearln()
            logger.error(result)
        # end if
        bar.next()
    # end for

    bar.finish()
    print('Processed %d chapters' % len(app.chapters))
# end def


def download_chapter_images(app):
    app.progress = 0

    # download or generate cover
    app.book_cover = download_cover(app)
    if not app.book_cover:
        app.book_cover = generate_cover(app)
    # end if
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
        image_output_path = os.path.join(app.output_path, 'images')
        for img in soup.select('img'):
            full_url = app.crawler.absolute_url(img['src'], page_url=chapter['url'])
            future = app.crawler.executor.submit(
                download_image,
                app,
                full_url,
                image_output_path
            )
            futures_to_check.setdefault(chapter['id'], [])
            futures_to_check[chapter['id']].append(future)
            image_count += 1
        # end for
    # end for

    if not futures_to_check:
        return
    # end if

    bar = IncrementalBar('Downloading images  ', max=image_count)
    if os.getenv('debug_mode') == 'yes':
        bar.next = lambda: None  # Hide in debug mode
        bar.finish()
    else:
        bar.start()
    # end if

    for chapter in app.chapters:
        if chapter['id'] not in futures_to_check:
            bar.next()
            continue
        # end if

        images = {}
        for future in futures_to_check[chapter['id']]:
            url, filename = future.result()
            bar.next()
            if filename:
                images[url] = filename
            # end if
        # end for

        soup = app.crawler.make_soup('<main>' + chapter['body'] + '</main>')
        for img in soup.select('img'):
            if img['src'] in images:
                filename = images[img['src']]
                img['src'] = 'images/%s' % filename
                img['style'] = 'float: left; margin: 15px; width: 100%;'
        # end for
        chapter['body'] = str(soup.select_one('main'))
    # end for

    bar.finish()
    print('Processed %d images' % image_count)
# end def
