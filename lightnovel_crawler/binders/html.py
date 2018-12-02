import logging
import os

from ..assets.html_style import get_value as get_css_style

logger = logging.getLogger('HTML_BINDER')


def bind_html_chapter(chapter, prev_chapter, next_chapter):
    prev_button = '%s.html' % (
        str(prev_chapter['id']).rjust(5, '0')) if prev_chapter else '#'
    next_button = '%s.html' % str(next_chapter['id']).rjust(
        5, '0') if next_chapter else '#'
    button_group = '<div class="link-group">'
    button_group += '<a class="btn" href="%s">Previous</a>' % prev_button
    # button_group += '<a href="%s" target="_blank">Original Source</a>' % chapter['url']
    button_group += '<a class="btn" href="%s">Next</a>' % next_button
    button_group += '</div>'

    script = '''
    window.addEventListener('scroll', function(e) {
        try {
            var scroll = window.scrollY;
            var height = document.body.scrollHeight - window.innerHeight + 10;
            var percent = Math.round(100.0 * scroll / height);
            document.getElementById('readpos').innerText = percent + '%';
        } catch (err) {
            // ignore
        }
    })
    '''

    html = '<!DOCTYPE html>\n'
    html += '<html><head>'
    html += '<meta charset="utf-8"/>'
    html += '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
    html += '<title>%s</title>' % chapter['title']
    html += '<style>%s</style>' % get_css_style()
    html += '<script>%s</script>' % script
    html += '</head><body><div id="content">'
    html += button_group
    html += '<main>%s</main>' % chapter['body']
    html += button_group
    html += '</div>'
    html += '<div id="readpos">0%</div>'
    html += '</body></html>'

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
