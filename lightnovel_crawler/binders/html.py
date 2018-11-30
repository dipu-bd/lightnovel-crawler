import logging
import os

logger = logging.getLogger('HTML_BINDER')


def bind_html_chapter(chapter, prev_chapter, next_chapter):
    with open(os.path.join(os.path.dirname(__file__), 'html_style.css')) as f:
        style = f.read()
    # end with
    prev_button = '%s.html' % (
        str(prev_chapter['id']).rjust(5, '0')) if prev_chapter else '#'
    next_button = '%s.html' % str(next_chapter['id']).rjust(
        5, '0') if next_chapter else '#'
    button_group = '''<div class="link-group">
        <a class="btn" href="%s">Previous</a>
        <a href="%s" target="_blank">Original Source</a>
        <a class="btn" href="%s">Next</a>
    </div>''' % (prev_button, chapter['url'], next_button)

    html = '<!DOCTYPE html>\n'
    html += '<html>\n<head>'
    html += '<meta charset="utf-8"/>'
    html += '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
    html += '<title>%s</title>' % chapter['title']
    html += '<style>%s</style>' % style
    html += '</head>\n<body>\n<div id="content">\n'
    html += button_group
    html += '<main>%s</main>' % chapter['body']
    html += button_group
    html += '\n</div>\n</body>\n</html>'

    file_name = '%s.html' % str(chapter['id']).rjust(5, '0')
    return html, file_name
# end def


def make_htmls(app, data):
    web_files = []
    for vol in data:
        dir_name = os.path.join(app.output_path, 'html', vol)
        os.makedirs(dir_name, exist_ok=True)
        for i in range(len(data[vol])):
            chapter = data[vol][i]
            prev_chapter = data[vol][i - 1] if i > 0 else None
            next_chapter = data[vol][i + 1] if i + 1 < len(data[vol]) else None
            html, file_name = bind_html_chapter(
                chapter, prev_chapter, next_chapter)

            file_name = os.path.join(dir_name, file_name)
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(html)
            # end with
            web_files.append(file_name)
        # end for
    # end for
    logger.warn('Created: %d html files', len(web_files))
    return web_files
# end def
