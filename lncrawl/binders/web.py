# -*- coding: utf-8 -*-
import logging
import os

from ..assets.html_script import get_value as get_js_script
from ..assets.html_style import get_value as get_css_style

logger = logging.getLogger(__name__)

def get_filename(chapter):
    if not chapter or 'id' not in chapter:
        return None
    return str(chapter['id']).rjust(5, '0') + '.html'
# end def

def bind_html_chapter(chapters, index, direction='ltr'):
    chapter = chapters[index]
    prev_chapter = chapters[index - 1] if index > 0 else None
    next_chapter = chapters[index + 1] if index + 1 < len(chapters) else None

    this_filename = get_filename(chapter)
    prev_filename = get_filename(prev_chapter)
    next_filename = get_filename(next_chapter)
    
    all_chapter_options = '\n'.join([
        f'''<option value="{get_filename(item)}" {"selected" if idx == index else ""}>{item["title"]}</option>'''
        for idx, item in enumerate(chapters)
    ])

    button_group = f'''
    <div class="link-group">
        <a class="btn prev-button" href="{prev_filename or '#'}">Previous</a>
        <select class="toc">{all_chapter_options}</select>
        <a class="btn next-button"  href="{next_filename or '#'}">Next</a>
    </div>
    '''
 
    main_body = chapter['body']
    if not main_body:
        main_body = f"<h1>{chapter['title']}</h1><p>No contents</p>"
    # end if

    html = f'''
    <!DOCTYPE html>
        <html dir="{direction}">
        <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>
            <title>{chapter['title']}</title>
            <style>
                {get_css_style()}
            </style>
            <script>
                {get_js_script()}
            </script>
        </head>
        <body>
            <div id="content">
                {button_group}
                <main>{main_body}</main>
                {button_group}
            </div>
            <div id="readpos">0%</div>
        </body>
    </html>
    '''

    return html, this_filename
# end def


def make_webs(app, data):
    web_files = []
    for vol in data:
        dir_name = os.path.join(app.output_path, 'web', vol)
        os.makedirs(dir_name, exist_ok=True)
        for i in range(len(data[vol])):
            direction = 'rtl' if app.crawler.is_rtl else 'ltr'
            html, file_name = bind_html_chapter(data[vol], i, direction)
            file_name = os.path.join(dir_name, file_name)
            with open(file_name, 'w', encoding='utf8') as file:
                file.write(html)
            # end with
            web_files.append(file_name)
        # end for
    # end for
    print('Created: %d web files' % len(web_files))
    return web_files
# end def
