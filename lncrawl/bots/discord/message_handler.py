# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import random
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import quote

import discord

from ...core.app import App
from ...utils.uploader import upload
from .config import max_workers, public_ip, public_path

logger = logging.getLogger(__name__)

available_formats = [
    'epub',
    'text',
    'web',
    'mobi',
    'pdf',
    'fb2',
]

disable_search = os.getenv('DISCORD_DISABLE_SEARCH') == 'true'


class MessageHandler:
    def __init__(self, client):
        self.app = App()
        self.client = client
        self.state = None
        self.executor = ThreadPoolExecutor(max_workers)
        self.last_activity = datetime.now()
        self.closed = False
        self.get_current_status = None
    # end def

    def process(self, message):
        self.last_activity = datetime.now()
        self.executor.submit(self.handle_message, message)
    # end def

    def destroy(self):
        try:
            self.get_current_status = None
            self.client.handlers.pop(str(self.user.id))
            self.send_sync('Closing current session...')
            self.executor.shutdown(wait=False)
            self.app.destroy()
            shutil.rmtree(self.app.output_path, ignore_errors=True)
        except Exception:
            logger.exception('While destroying MessageHandler')
        finally:
            self.send_sync('Session closed. Send *start* to start over')
            self.closed = True
        # end try
    # end def

    def handle_message(self, message):
        self.message = message
        self.user = message.author
        if not self.state:
            self.state = self.get_novel_url
        # end if
        try:
            self.state()
        except Exception as ex:
            logger.exception('Failed to process state')
            self.send_sync('Something went wrong!\n`%s`' % str(ex))
            self.executor.submit(self.destroy)
        # end try
    # end def

    # ---------------------------------------------------------------------- #

    def wait_for(self, async_coroutine):
        asyncio.run_coroutine_threadsafe(
            async_coroutine,
            self.client.loop
        ).result()
    # end def3

    async def send(self, *contents):
        if self.closed:
            return
        self.last_activity = datetime.now()
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

        status = None
        if callable(self.get_current_status):
            status = self.get_current_status()
        # end if
        if not status:
            status = random.choice([
                'Send !cancel to stop this session.',
                'Please wait...',
                'Processing, give me more time...',
                'A little bit longer...',
            ])
        # end if

        self.send_sync(status)
    # end def

    # ---------------------------------------------------------------------- #

    def get_novel_url(self):
        self.state = self.busy_state
        if disable_search:
            self.send_sync(
                'Send me an URL of novel info page with chapter list!'
            )
        else:
            self.send_sync(
                'I recognize these two categories:\n'
                '- Profile page url of a lightnovel.\n'
                '- A query to search your lightnovel.',
                'What are you looking for?'
            )
        # end if
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
            logger.exception("Fail to init crawler")
            self.send_sync('\n'.join([
                'Sorry! I do not recognize this sources yet.',
                'See list of supported sources here:',
                'https://github.com/dipu-bd/lightnovel-crawler#c3-supported-sources',
            ]))
            self.get_novel_url()
        # end try

        if self.app.crawler:
            self.send_sync('Got your page link')
            self.get_novel_info()
        elif self.app.user_input and len(self.app.user_input) < 4:
            self.send_sync('Your query is too short')
            self.state = self.handle_novel_url
            self.get_novel_url()
        else:
            if disable_search:
                self.send_sync(
                    'Sorry! I can not do searching.\n'
                    'Please use Google to find your novel first'
                )
                self.get_novel_url()
            else:
                self.send_sync(
                    'Searching %d sources for "%s"\n' % (
                        len(self.app.crawler_links), self.app.user_input),
                )
                self.display_novel_selection()
            # end if
        # end if
    # end def

    # ------------------------------------------------------------ #
    # SEARCHING -- skips if DISCORD_DISABLE_SEARCH is 'true'
    # ------------------------------------------------------------ #

    def get_novel_selection_progres(self):
        return 'Searched %d of %d sources' % (self.app.progress, len(self.app.crawler_links))
    # end def

    def display_novel_selection(self):
        self.get_current_status = self.get_novel_selection_progres
        self.app.search_novel()
        self.get_current_status = None
        if self.closed:
            return

        if len(self.app.search_results) == 0:
            self.send_sync('No novels found for "%s"' % self.app.user_input)
            self.state = self.handle_novel_url
        elif len(self.app.search_results) == 1:
            self.selected_novel = self.app.search_results[0]
            self.display_sources_selection()
        else:
            self.send_sync('\n'.join([
                'Found %d novels:' % len(self.app.search_results)
            ] + [
                '%d. **%s** `%d sources`' % (
                    i + 1,
                    item['title'],
                    len(item['novels'])
                ) for i, item in enumerate(self.app.search_results)
            ] + [
                '',
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
        novel_list = self.selected_novel['novels']
        self.send_sync('**%s** is found in %d sources:\n' %
                       (self.selected_novel['title'], len(novel_list)))

        for j in range(0, len(novel_list), 10):
            self.send_sync('\n'.join([
                '%d. <%s> %s' % (
                    (j + i + 1),
                    item['url'],
                    item['info'] if 'info' in item else ''
                ) for i, item in enumerate(novel_list[j:j+10])
            ]))
        # end for

        self.send_sync('\n'.join([
            '',
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
                'Sorry! You should select *one* source '
                'from the list (%d selected).' % match_count
            )
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
        # TODO: Handle login here

        self.send_sync('Getting information about your novel...')
        self.executor.submit(self.download_novel_info)
    # end def

    def download_novel_info(self):
        self.state = self.busy_state
        try:
            self.get_current_status = lambda: 'Getting novel information...'
            self.app.get_novel_info()
            if self.closed:
                return
        except Exception as ex:
            logger.exception('Failed to get novel info')
            self.send_sync('Failed to get novel info.\n`%s`' % str(ex))
            self.executor.submit(self.destroy)
            return
        # end try

        # Setup output path
        root = os.path.abspath('.discord_bot_output')
        if public_path and os.path.exists(public_path):
            root = os.path.abspath(public_path)
        # end if
        good_name = os.path.basename(self.app.output_path)
        output_path = os.path.join(root, str(self.user.id), good_name)
        shutil.rmtree(output_path, ignore_errors=True)
        
        os.makedirs(output_path, exist_ok=True)
        self.app.output_path = output_path

        self.display_range_selection()
    # end def

    def display_range_selection(self):
        self.send_sync('\n'.join([
            'Now you choose what to download:',
            '- Send `!cancel` to stop this session.',
            '- Send `all` to download all chapters',
            '- Send `last 20` to download last 20 chapters. Choose any number you want.',
            '- Send `first 10` for first 10 chapters. Choose any number you want.',
            '- Send `volume 2 5` to download download volume 2 and 5. Pass as many numbers you need.',
            '- Send `chapter 110 120` to download chapter 110 to 120. Only two numbers are accepted.',
        ]))
        self.send_sync(
            '**It has `%d` volumes and `%d` chapters.**' % (
                len(self.app.crawler.volumes),
                len(self.app.crawler.chapters)
            )
        )
        self.state = self.handle_range_selection
    # end def

    def handle_range_selection(self):
        self.state = self.busy_state
        text = self.message.content.strip().lower()
        if text == '!cancel':
            self.executor.submit(self.destroy)
            return
        # end if

        if text == 'all':
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
            '- Send `!all` to download all formats _(it may take a very long time!)_',
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

        if text == '!all':
            output_format = set(available_formats)
        else:
            output_format = set(re.findall('|'.join(available_formats), text.lower()))
        # end if

        if not len(output_format):
            self.send_sync('Sorry! I did not recognize your input. '
                           'Try one of these: `' + '` `'.join(available_formats) + '`')
            self.state = self.handle_output_selection
            return
        # end if

        self.app.output_formats = {x: (x in output_format) for x in available_formats}
        self.send_sync('I will generate e-book in (%s) format' % (', ' .join(output_format)))

        self.send_sync('\n'.join([
            'Starting download...',
            'Send anything to view status.',
            'Send `!cancel` to stop it.',
        ]))

        self.executor.submit(self.start_download)
    # end def

    # ---------------------------------------------------------------------- #

    def get_download_progress_status(self):
        return 'Downloaded %d of %d chapters' % (self.app.progress, len(self.app.chapters))
    # end def

    def start_download(self):
        self.app.pack_by_volume = False

        try:
            self.send_sync(
                '**%s**' % self.app.crawler.novel_title,
                'Downloading %d chapters...' % len(self.app.chapters),
            )
            self.get_current_status = self.get_download_progress_status
            self.app.start_download()
            self.get_current_status = None
            if self.closed:
                return

            self.get_current_status = lambda: 'Binding books... %.0f%%' % (self.app.progress)
            self.send_sync('Binding books...')
            self.app.bind_books()
            self.get_current_status = None
            if self.closed:
                return

            self.send_sync('Compressing output folder...')
            self.app.compress_books()
            if self.closed:
                return

            if public_ip and public_path and os.path.exists(public_path):
                self.send_sync('Publishing files...')
                self.publish_files()
            else:
                for archive in self.app.archived_outputs:
                    self.upload_file(archive)
                # end for
            # end if
        except Exception as ex:
            logger.exception('Failed to download')
            self.send_sync('Download failed!\n`%s`' % str(ex))
        finally:
            self.executor.submit(self.destroy)
        # end try
    # end def

    def publish_files(self):
        try:
            download_url = '%s/%s/%s' % (public_ip.strip('/'),
                                         quote(str(self.user.id)),
                                         quote(os.path.basename(self.app.output_path)))
            self.send_sync('Download files from:\n' + download_url)
        except Exception:
            logger.exception('Fail to publish')
        # end try
    # end def

    def upload_file(self, archive):
        # Check file size
        filename = os.path.basename(archive)
        file_size = os.stat(archive).st_size
        if file_size > 7.99 * 1024 * 1024:
            self.send_sync(f'File {filename} exceeds 8MB. Using alternative cloud storage.')
            try:
                description = 'Generated By : Lightnovel Crawler Discord Bot'
                direct_link = upload(archive, description)
                self.send_sync(direct_link)
            except Exception as e:
                logger.error('Failed to upload file: %s', archive, e)
                self.send_sync(f'Failed to upload file: {filename}.\n`Error: {e}`')
            # end if
            return

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
    # end def
# end class
