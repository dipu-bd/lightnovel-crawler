# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import random
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import discord

from ...binders import available_formats
from ...core.app import App
from ...sources import crawler_list
from ...utils.uploader import upload
from .config import max_workers, public_ip, public_path

logger = logging.getLogger('DISCORD_BOT')


class MessageHandler:
    def __init__(self, client):
        self.app = App()
        self.client = client
        self.state = None
        self.executor = ThreadPoolExecutor(max_workers)
    # end def

    def process(self, message):
        self.executor.submit(self.handle_message, message)
    # end def

    def destroy(self):
        try:
            self.client.handlers.pop(str(self.user.id))
            self.send_sync('Closing current session...')
            self.executor.shutdown(wait=False)
            self.app.destroy()
            shutil.rmtree(self.app.output_path, ignore_errors=True)
        except Exception:
            logger.exception('While destroying MessageHandler')
        finally:
            self.send_sync('Session closed. Send *start* to start over')
        # end try
    # end def

    def handle_message(self, message):
        self.message = message
        self.user = message.author
        if not self.state:
            self.state = self.get_novel_url
        # end if
        self.state()
    # end def

    # ---------------------------------------------------------------------- #

    def wait_for(self, async_coroutine):
        asyncio.run_coroutine_threadsafe(
            async_coroutine,
            self.client.loop
        ).result()
    # end def3

    async def send(self, *contents):
        async with self.user.typing():
            for text in contents:
                if not text:
                    continue
                # end if
                await self.user.send(text)
            # end for
        # end with
    # end def

    def send_sync(self, *contents):
        self.wait_for(self.send(*contents))
    # end def

    def busy_state(self):
        text = self.message.content.strip()

        if text == '!cancel':
            self.executor.submit(self.destroy)
            return
        # end if

        self.send_sync(random.choice([
            'Please wait...',
            'Processing, please give me time...',
            'I am just a bot. Please be patient...',
            'A little bit longer...'
        ]))
    # end def

    # ---------------------------------------------------------------------- #

    def get_novel_url(self):
        self.state = self.busy_state
        self.send_sync(
            'I recognize these two categories:\n'
            '- Profile page url of a lightnovel.\n'
            '- A query to search your lightnovel.',
            'What are you looking for?'
        )
        self.state = self.handle_novel_url
    # end def

    def handle_novel_url(self):
        self.state = self.busy_state

        text = self.message.content.strip()
        if text == '!cancel':
            self.executor.submit(self.destroy)
            return
        # end if

        try:
            self.app.user_input = self.message.content.strip()
            self.app.init_search()
        except Exception:
            self.send_sync('\n'.join([
                'Sorry! I do not recognize this sources yet.',
                'See list of supported sources here:',
                'https://github.com/dipu-bd/lightnovel-crawler#c3-supported-sources',
            ]))
            self.get_novel_url()
        # end try

        if len(self.app.user_input) < 4:
            self.send_sync('Your query is too short')
            self.state = self.handle_novel_url
            return
        # end if

        if self.app.crawler:
            self.send_sync('Got your page link')
            self.get_novel_info()
        else:
            self.send_sync(
                'Searching %d sources for "%s"\n' % (
                    len(self.app.crawler_links), self.app.user_input),
            )
            self.display_novel_selection()
        # end if
    # end def

    def display_novel_selection(self):
        self.app.search_novel()

        if len(self.app.search_results) == 0:
            self.send_sync('No novels found for "%s"' % self.app.user_input)
            self.state = self.handle_novel_url
        elif len(self.app.search_results) == 1:
            self.selected_novel = self.app.search_results[0]
            self.display_sources_selection()
        else:
            self.send_sync('\n'.join([
                'Found %d novels:\n' % len(self.app.search_results)
            ] + [
                '%d. **%s** `%d sources`' % (
                    i + 1,
                    item['title'],
                    len(item['novels'])
                ) for i, item in enumerate(self.app.search_results)
            ] + [
                'Enter name or index of your novel.',
                'Send `!cancel` to stop this session.'
            ]))
            self.state = self.handle_novel_selection
        # end if
    # end def

    def handle_novel_selection(self):
        self.state = self.busy_state

        text = self.message.content.strip()
        if text.startswith('!cancel'):
            self.get_novel_url()
            return
        # end if

        match_count = 0
        selected = None
        for i, res in enumerate(self.app.search_results):
            if str(i + 1) == text:
                selected = res
                match_count += 1
            elif text.isdigit() or len(text) < 3:
                pass
            elif res['title'].lower().find(text) != -1:
                selected = res
                match_count += 1
            # end if
        # end for

        if match_count != 1:
            self.send_sync(
                'Sorry! You should select *one* novel from the list (%d selected).' % match_count)
            self.display_novel_selection()
            return
        # end if

        self.selected_novel = selected
        self.display_sources_selection()
    # end def

    def display_sources_selection(self):
        self.send_sync('\n'.join([
            '**%s** is found in %d sources:\n' % (
                self.selected_novel['title'], len(self.selected_novel['novels']))
        ] + [
            '%d. <%s> %s' % (
                i + 1,
                item['url'],
                item['info'] if 'info' in item else ''
            ) for i, item in enumerate(self.selected_novel['novels'])
        ] + [
            'Enter index or name of your source.',
            'Send `!cancel` to stop this session.',
        ]))
        self.state = self.handle_sources_to_search
    # end def

    def handle_sources_to_search(self):
        self.state = self.busy_state

        if len(self.selected_novel['novels']) == 1:
            novel = self.selected_novel['novels'][0]
            return self.handle_search_result(novel)
        # end if

        text = self.message.content.strip()
        if text.startswith('!cancel'):
            return self.get_novel_url()
        # end if

        match_count = 0
        selected = None
        for i, res in enumerate(self.selected_novel['novels']):
            if str(i + 1) == text:
                selected = res
                match_count += 1
            elif text.isdigit() or len(text) < 3:
                pass
            elif res['url'].lower().find(text) != -1:
                selected = res
                match_count += 1
            # end if
        # end for

        if match_count != 1:
            self.send_sync(
                'Sorry! You should select *one* source from the list (%d selected).' % match_count)
            return self.display_sources_selection()
        # end if

        self.handle_search_result(selected)
    # end def

    def handle_search_result(self, novel):
        self.send_sync('Selected: %s' % novel['url'])
        self.app.init_crawler(novel['url'])
        self.get_novel_info()
    # end def

    # ---------------------------------------------------------------------- #

    def get_novel_info(self):
        if not self.app.crawler:
            self.send_sync('Could not find any crawler to get your novel')
            self.state = self.get_novel_info
            return
        # end if

        # TODO: Handle login here

        self.send_sync('Getting information about your novel...')
        self.executor.submit(self.download_novel_info)
    # end def

    def download_novel_info(self):
        self.state = self.busy_state
        self.app.get_novel_info()

        # Setup output path
        good_name = os.path.basename(self.app.output_path)
        output_path = os.path.abspath(
            os.path.join('.discord_bot_output', str(self.user.id), good_name))
        if os.path.exists(output_path):
            shutil.rmtree(output_path, ignore_errors=True)
        # end if

        os.makedirs(output_path, exist_ok=True)
        self.app.output_path = output_path

        self.display_range_selection()
    # end def

    def display_range_selection(self):
        self.send_sync(
            'It has %d volumes and %d chapters.' % (
                len(self.app.crawler.volumes),
                len(self.app.crawler.chapters)
            )
        )
        self.send_sync('\n'.join([
            'Now you choose what to download:',
            '- Send `!cancel` to stop this session.',
            '- To download everyhting send `!all`',
            '- Send `last 20` to download last 20 chapters. Choose any number you want.',
            '- Send `first 10` for first 10 chapters. Choose any number you want.',
            '- Send `volume 2 5` to download download volume 2 and 5. Pass as many numbers you need.',
            '- Send `chapter 110 120` to download chapter 110 to 120. Only two numbers are accepted.',
        ]))
        self.state = self.handle_range_selection
    # end def

    def handle_range_selection(self):
        self.state = self.busy_state
        text = self.message.content.strip()
        if text == '!cancel':
            self.get_novel_url()
            return
        # end if
        if text == '!all':
            self.app.chapters = self.app.crawler.chapters[:]
        elif re.match(r'^first(\s\d+)?$', text):
            text = text[len('first'):].strip()
            n = int(text) if text.isdigit() else 50
            n = 50 if n < 0 else n
            self.app.chapters = self.app.crawler.chapters[: n]
        elif re.match(r'^last(\s\d+)?$', text):
            text = text[len('last'):].strip()
            n = int(text) if text.isdigit() else 50
            n = 50 if n < 0 else n
            self.app.chapters = self.app.crawler.chapters[-n:]
        elif re.match(r'^volume(\s\d+)+$', text):
            text = text[len('volume'):].strip()
            selected = re.findall(r'\d+', text)
            self.send_sync(
                'Selected volumes: ' + ', '.join(selected),
            )
            selected = [int(x) for x in selected]
            self.app.chapters = [
                chap for chap in self.app.crawler.chapters
                if selected.count(chap['volume']) > 0
            ]
        elif re.match(r'^chapter(\s\d+)+$', text):
            text = text[len('chapter'):].strip()
            pair = text.split(' ')
            if len(pair) == 2:
                def resolve_chapter(name):
                    cid = 0
                    if name.isdigit():
                        cid = int(name)
                    else:
                        cid = self.app.crawler.get_chapter_index_of(name)
                    # end if
                    return cid - 1
                # end def
                first = resolve_chapter(pair[0])
                second = resolve_chapter(pair[1])
                if first > second:
                    second, first = first, second
                # end if
                if first >= 0 or second < len(self.app.crawler.chapters):
                    self.app.chapters = self.app.crawler.chapters[first: second]
                # end if
            # end if
            if len(self.app.chapters) == 0:
                self.send_sync('Chapter range is not valid. Please try again')
                self.state = self.handle_range_selection
                return
            # end if
        else:
            self.send_sync(
                'Sorry! I did not recognize your input. Please try again')
            self.state = self.handle_range_selection
            return
        # end if

        if len(self.app.chapters) == 0:
            self.send_sync(
                'You have not selected any chapters. Please select at least one')
            self.state = self.handle_range_selection
            return
        # end if

        self.send_sync('Got your range selection')
        self.display_output_selection()
    # end def

    def display_output_selection(self):
        self.state = self.busy_state
        self.send_sync('\n'.join([
            'Now you can choose book formats to download:',
            '- Send `!cancel` to stop.',
            # '- Send `!all` to download all formats _(it may take a very very long time!)_',
            'To select specific output formats:',
            '- Send `pdf` to download only pdf format',
            '- Send `epub pdf` to download both epub and pdf formats.',
            '- Send `{space separated format names}` for multiple formats',
            'Available formats: `' + '` `'.join(available_formats) + '`',
        ]))
        self.state = self.handle_output_selection
    # end def

    def handle_output_selection(self):
        self.state = self.busy_state

        text = self.message.content.strip()
        if text.startswith('!cancel'):
            self.get_novel_url()
            return
        # end if
        if text.startswith('!all'):
            self.app.output_formats = None
        else:
            output_format = set(re.findall(
                '|'.join(available_formats),
                text.lower()
            ))
            if len(output_format):
                self.app.output_formats = {
                    x: (x in output_format)
                    for x in available_formats
                }
                self.send_sync('I will generate e-book in (%s) format' %
                               (', ' .join(output_format)))
            else:
                self.send_sync(
                    'Sorry! I did not recognize your input. Please try again')
                self.state = self.handle_output_selection
                return
            # end if
        # end if

        self.send_sync('\n'.join([
            'Starting download...',
            'Send anything to view status.',
            'Send `!cancel` to stop it.',
        ]))

        self.executor.submit(self.start_download)
    # end def

    # ---------------------------------------------------------------------- #

    def start_download(self):
        self.app.pack_by_volume = False

        self.send_sync(
            '**%s**' % self.app.crawler.novel_title,
            'Downloading %d chapters...' % len(self.app.chapters),
        )
        self.app.start_download()
        self.send_sync('Download complete.')

        self.send_sync('Binding books...')
        self.app.bind_books()
        self.send_sync('Book binding completed.')

        self.send_sync('Compressing output folder...')
        self.app.compress_output()
        self.send_sync('Compressed output folder.')

        if public_ip and public_path and os.path.exists(public_path):
            self.send_sync('Publishing files...')
            self.publish_files()
        else:
            self.send_sync('Uploading files...')
            for archive in self.app.archived_outputs:
                self.upload_file(archive)
            # end for
        # end if

        self.executor.submit(self.destroy)
    # end def

    def publish_files(self):
        try:
            folder = os.path.join(public_path,
                                  str(self.user.id),
                                  self.app.good_file_name)
            logger.info("Publish folder: %s", folder)

            os.makedirs(folder, exist_ok=True)
            download_url = '%s/%s/%s' % (public_ip.strip('/'),
                                         quote(str(self.user.id)),
                                         quote(self.app.good_file_name))
            logger.info("Download url: %s", download_url)

            urls = []
            for src in self.app.archived_outputs:
                file_name = os.path.basename(src)
                dst = os.path.join(folder, file_name)
                shutil.copy(src, dst)
                urls.append(download_url + '/' + quote(file_name))
            # end for

            self.send_sync('\n'.join(['Download files from:'] + urls))
        except Exception:
            logger.exception('Fail to publish')
        # end try
    # end def

    def upload_file(self, archive):
        # Check file size
        file_size = os.stat(archive).st_size
        if file_size > 7.99 * 1024 * 1024:
            self.send_sync(
                'File %s exceeds 8MB. Uploading To Google Drive.' % os.path.basename(archive))
            description = 'Generated By : Discord Bot Ebook Smelter'
            link_id = upload(archive, description)
            if link_id:
                self.send_sync('https://drive.google.com/open?id=%s' % link_id)
            else:
                self.send_sync('Failed to upload to google drive')
            # end if
        else:
            # Upload small files to discord directly
            k = 0
            while(file_size > 1024 and k < 3):
                k += 1
                file_size /= 1024.0
            # end while
            self.send_sync(
                'Uploading %s [%d%s] ...' % (
                    os.path.basename(archive),
                    int(file_size * 100) / 100.0,
                    ['B', 'KB', 'MB', 'GB'][k]
                )
            )
            self.wait_for(
                self.user.send(
                    file=discord.File(
                        open(archive, 'rb'),
                        os.path.basename(archive)
                    )
                )
            )
        # end if
    # end def
# end class
