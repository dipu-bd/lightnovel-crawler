#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio
import discord

from ..core.app import App
from ..spiders import crawler_list
from ..utils.uploader import upload
from ..binders import available_formats

logger = logging.getLogger('DISCORD_BOT')


class DiscordBot(discord.Client):
    # Store user message handlers
    handlers = dict()
    # The special signal character for crawler commands
    signal = os.getenv('DISCORD_SIGNAL_CHAR') or '!'

    def start_bot(self):
        self.run(os.getenv('DISCORD_TOKEN'))
    # end def

    @asyncio.coroutine
    async def on_ready(self):
        print('Discord bot in online!')
        activity = discord.Game(name="🔥Ready For Smelting🔥")
        await self.change_presence(status=discord.Status.online, activity=activity)
    # end def

    @asyncio.coroutine
    async def on_message(self, message):
        if message.author == self.user:
            return  # I am not crazy to talk with myself
        # end if
        if message.author.bot:
            return  # Other bots are not edible
        # end if
        if isinstance(message.channel, discord.abc.PrivateChannel):
            await self.handle_message(message)
        elif message.content == '!help':
            await self.send_public_text(
                message,
                'Enter `%slncrawl` to start a new session of **Lightnovel Crawler**' % self.signal
            )
        elif message.content == self.signal + 'lncrawl':
            uid = message.author.id
            await self.send_public_text(
                message, "I will message you privately <@%s>" % uid)
            handler = self.handlers.get(uid)
            if handler:
                handler.destroy()
            # end if
            await self.handle_message(message)
        else:
            return  # It goes over the head
        # end if
    # end def

    async def send_public_text(self, message, text):
        async with message.channel.typing():
            await message.channel.send(text)
    # end def

    async def handle_message(self, message):
        try:
            user = message.author
            handler = self.init_handler(user.id)
            await handler.process(message)
        except Exception as err:
            logger.exception('While handling this message: %s', message)
            try:
                await message.channel.send(
                    'Sorry! We had some trouble processing your request. Please try again.\n\n' +
                    'Report [here](https://github.com/dipu-bd/lightnovel-crawler/issues/new/choose)' +
                    ' if this problem continues with this message: `' +
                    str(err) + '`'
                )
            except Exception:
                pass  # this world is doomed!!
            # end try
        # end try
    # end def

    def init_handler(self, uid):
        if not self.handlers.get(uid):
            self.handlers[uid] = MessageHandler(self)
        # end if
        return self.handlers.get(uid)
    # end def
# end def


class MessageHandler:
    def __init__(self, client):
        self.app = App()
        self.client = client
        self.state = None
        self.executors = ThreadPoolExecutor(1)
    # end def

    def destroy(self):
        try:
            self.app.destroy()
            self.executors.shutdown(False)
        except Exception:
            logger.exception('While destroying MessageHandler')
        finally:
            self.client.handlers.pop(self.user.id)
            shutil.rmtree(self.app.output_path, ignore_errors=True)
        # end try
    # end def

    @asyncio.coroutine
    async def send(self, *contents):
        for text in contents:
            if text:
                # await self.client.send_typing(self.user)
                async with self.user.typing():
                    await self.user.send(text)
            # end if
        # end for
    # end def

    @asyncio.coroutine
    async def process(self, message):
        self.message = message
        self.user = message.author
        if not self.state:
            await self.send(
                '-' * 80 + '\n' +
                ('Hello %s\n' % self.user.name) +
                '*Lets make reading lightnovels great again!*\n' +
                '-' * 80 + '\n'
            )
            self.state = self.get_novel_url
        # end if
        await self.state()
    # end def

    async def get_novel_url(self):
        await self.send(
            'I recognize these two categories:\n'
            '- Profile page url of a lightnovel.\n'
            '- A query to search your lightnovel.',
            'What are you looking for?'
        )
        self.state = self.handle_novel_url
    # end def

    async def handle_novel_url(self):
        try:
            self.app.user_input = self.message.content.strip()
            self.app.init_search()
        except Exception:
            await self.send(
                'Sorry! I only know these sources:\n' +
                '\n'.join(['- %s' % x for x in crawler_list.keys()]),
                'Enter something again.')
        # end try
        if len(self.app.user_input) < 4:
            await self.send('Your query is too short')
            return
        # end if

        if self.app.crawler:
            await self.send('Got your page link')
            await self.get_novel_info()
        else:
            await self.send(
                'Searching %d sources for "%s"\n' % (
                    len(self.app.crawler_links), self.app.user_input),
                'Please do not type anything before I reply!'
            )
            await self.display_novel_selection()
        # end if
    # end def

    async def display_novel_selection(self):
        async with self.user.typing():
            self.app.search_novel()

            if len(self.app.search_results) == 0:
                await self.send('No novels found for "%s"' % self.app.user_input)
                return
            # end if
            if len(self.app.search_results) == 1:
                self.selected_novel = self.app.search_results[0]
                await self.display_sources_selection()
                return
            # end if

            await self.send(
                ('Found %d novels:\n' % len(self.app.search_results)) +
                '\n'.join([
                    '%d. **%s** `%d sources`' % (
                        i + 1,
                        item['title'],
                        len(item['novels'])
                    ) for i, item in enumerate(self.app.search_results)
                ]) + '\n' +
                'Enter name or index of your novel.\n' +
                'Send `!cancel` to stop this session.'
            )
            self.state = self.handle_novel_selection
    # end def

    async def handle_novel_selection(self):
        text = self.message.content.strip()
        if text.startswith('!cancel'):
            await self.get_novel_url()
            return
        # end if

        async with self.user.typing():
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
                await self.send(
                    'Sorry! You should select *one* novel from the list (%d selected).' % match_count)
                await self.display_novel_selection()
                return
            # end if

            self.selected_novel = selected
            await self.display_sources_selection()
    # end def

    async def display_sources_selection(self):
        async with self.user.typing():
            await self.send(
                (
                    '**%s** is found in %d sources:\n' % (
                        self.selected_novel['title'], len(self.selected_novel['novels']))
                ) + '\n'.join([
                    '%d. <%s> %s' % (
                        i + 1,
                        item['url'],
                        item['info'] if 'info' in item else ''
                    ) for i, item in enumerate(self.selected_novel['novels'])
                ]) + '\n' +
                'Enter index or name of your source.\n' +
                'Send `!cancel` to stop this session.'
            )
        self.state = self.handle_sources_to_search
    # end def

    async def handle_sources_to_search(self):
        if len(self.selected_novel['novels']) == 1:
            novel = self.selected_novel['novels'][0]
            await self.handle_search_result(novel)
            return
        # end if

        text = self.message.content.strip()
        if text.startswith('!cancel'):
            await self.get_novel_url()
            return
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
            await self.send(
                'Sorry! You should select *one* source from the list (%d selected).' % match_count)
            await self.display_sources_selection()
            return
        # end if

        await self.handle_search_result(selected)
    # end def

    async def handle_search_result(self, novel):
        await self.send('Selected: %s' % novel['url'])
        self.app.init_crawler(novel['url'])
        await self.get_novel_info()
    # end def

    async def get_novel_info(self):
        if not self.app.crawler:
            await self.send('Could not find any crawler to get your novel')
            self.state = self.get_novel_info
            return
        # end if

        # TODO: Handle login here

        await self.send('Getting information about your novel...')
        async with self.user.typing():
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

            # Get chapter range
            await self.send(
                'It has %d volumes and %d chapters.' % (
                    len(self.app.crawler.volumes),
                    len(self.app.crawler.chapters)
                )
            )

        await self.display_range_selection()
    # end def

    async def display_range_selection(self):
        await self.send('\n'.join([
            'Now you can send the following commands to modify what to download:',
            '- To download everything send `!all` or pass `!cancel` to stop.',
            '- Send `!last` followed by a number to download last few chapters. '
            'If it does not followed by a number, last 50 chapters will be downloaded.',
            '- Similarly you can send `!first` followed by a number to get first few chapters.',
            '- Send `!volume` followed by volume numbers to download.',
            '- To download a range of chatpers, Send `!chapter` followed by ' +
            'two chapter numbers or urls separated by *space*. ' +
            ('Chapter number must be between 1 and %d, ' % len(self.app.crawler.chapters)) +
            ('and chapter urls should be from <%s>.' %
             (self.app.crawler.home_url))
        ]))
        self.state = self.handle_range_selection
    # end def

    async def handle_range_selection(self):
        text = self.message.content.strip()
        if text.startswith('!cancel'):
            await self.get_novel_url()
            return
        # end if
        if text.startswith('!all'):
            self.app.chapters = self.app.crawler.chapters[:]
        elif text.startswith('!first'):
            text = text[len('!first'):].strip()
            n = int(text) if text.isdigit() else 50
            n = 50 if n < 0 else n
            self.app.chapters = self.app.crawler.chapters[:n]
        elif text.startswith('!last'):
            text = text[len('!last'):].strip()
            n = int(text) if text.isdigit() else 50
            n = 50 if n < 0 else n
            self.app.chapters = self.app.crawler.chapters[-n:]
        elif text.startswith('!volume'):
            text = text[len('!volume'):].strip()
            selected = re.findall(r'\d+', text)
            await self.send(
                'Selected volumes: ' + ', '.join(selected),
            )
            selected = [int(x) for x in selected]
            self.app.chapters = [
                chap for chap in self.app.crawler.chapters
                if selected.count(chap['volume']) > 0
            ]
        elif text.startswith('!chapter'):
            text = text[len('!chapter'):].strip()
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
                    self.app.chapters = self.app.crawler.chapters[first:second]
                # end if
            # end if
            if len(self.app.chapters) == 0:
                await self.send('Chapter range is not valid. Please try again')
                return
            # end if
        else:
            await self.send('Sorry! I did not recognize your input. Please try again')
            return
        # end if

        if len(self.app.chapters) == 0:
            await self.send('You have not selected any chapters. Please select at least one')
            return
        # end if

        await self.send('Got your range selection')
        await self.display_output_selection()
    # end def

    async def display_output_selection(self):
        await self.send('\n'.join([
            'Now you can choose book formats to download:',
            '- Send `!cancel` to stop.',
            '- Send `!all` to download all formats _(it may take a very very long time!)_',
            'To select specific output formats:',
            '- Send `pdf` to download only pdf format',
            '- Send `mobi pdf` to download both pdf and mobi formats.',
            '- Send `{space separated format names}` for multiple formats',
            'Available formats: `' + '` `'.join(available_formats) + '`',
        ]))
        self.state = self.handle_output_selection
    # end def

    async def handle_output_selection(self):
        text = self.message.content.strip()
        if text.startswith('!cancel'):
            await self.get_novel_url()
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
                await self.send('I will generate e-book in (%s) format' % (', ' .join(output_format)))
            else:
                await self.send('Sorry! I did not recognize your input. Please try again')
                return
            # end if
        # end if

        await self.send('\n'.join([
            'Starting download...',
            'Send anything to view status.',
            'Send `!cancel` to stop it.',
        ]))

        self.status = ['', '']
        self.state = self.report_download_progress
        try:
            self.executors.submit(self.start_download)
        except Exception:
            logger.exception('Download failure: %s', self.user.id)
        # end try
    # end def

    def start_download(self):
        self.app.pack_by_volume = False

        self.status = ['**%s**' % self.app.crawler.novel_title]
        self.status.append('Downloading %d chapters...' % len(self.app.chapters))
        self.app.start_download()

        self.status.append('Binding books...')
        self.app.bind_books()
        self.status[-1] = 'Book binding completed.'

        self.status.append('Compressing output folder...')
        self.app.compress_output()
        self.status[-1] = 'Compressed output folder.'

        self.status.append('Uploading files...')
        for archive in self.app.archived_outputs:
            asyncio.run_coroutine_threadsafe(
                self.upload_file(archive),
                self.client.loop
            ).result()
        # end for

        self.destroy()
    # end def

    async def upload_file(self, archive):
        file_size = os.stat(archive).st_size
        if file_size > 7.99 * 1024 * 1024:
            await self.send('File %s exceeds 8MB. Uploading To Google Drive.' % os.path.basename(archive))
            description = 'Generated By : Discord Bot Ebook Smelter'
            link_id = upload(archive, description)
            if link_id:
                await self.send('https://drive.google.com/open?id=%s' % link_id)
            else:
                await self.send('Failed to upload to google drive')
            # end if
        else:
            k = 0
            while(file_size > 1024 and k < 3):
                k += 1
                file_size /= 1024.0
            # end while
            await self.send(
                'Uploading %s [%d%s] ...' % (
                    os.path.basename(archive),
                    int(file_size * 100) / 100.0,
                    ['B', 'KB', 'MB', 'GB'][k]
                )
            )
            async with self.user.typing():
                # await message.channel.send('Hello', file=discord.File('cool.png', 'testing.png'))
                await self.user.send(
                    'Here you go ! ',
                    file=discord.File(
                        open(archive, 'rb'),
                        os.path.basename(archive)
                    )
                )
        # end if
    # end def

    async def report_download_progress(self):
        text = self.message.content.strip()

        if text == '!cancel':
            await self.send('Closing the session')
            self.destroy()
            await self.send('Session is now closed. Type *anything* to create a new one.')
            return
        # end if

        async with self.user.typing():
            if self.app.progress < len(self.app.chapters):
                self.status[1] = '%d out of %d chapters has been downloaded.' % (
                    self.app.progress, len(self.app.chapters))
            else:
                self.status[1] = 'Download complete.'
            # end if

            await self.send(
                '\n'.join(self.status).strip() + '\n\n' +
                'Send `!cancel` to stop'
            )
    # end def
# end class
