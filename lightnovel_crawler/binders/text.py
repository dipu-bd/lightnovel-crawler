import logging
import os
import re

from bs4 import BeautifulSoup

logger = logging.getLogger('TEXT_BINDER')


def make_texts(app, data):
    text_files = []
    for vol in data:
        dir_name = os.path.join(app.output_path, 'text', vol)
        os.makedirs(dir_name, exist_ok=True)
        for chap in data[vol]:
            file_name = '%s.txt' % str(chap['id']).rjust(5, '0')
            file_name = os.path.join(dir_name, file_name)
            with open(file_name, 'w', encoding='utf-8') as file:
                body = chap['body'].replace('</p><p', '</p>\n<p')
                soup = BeautifulSoup(body, 'lxml')
                text = '\n\n'.join(soup.stripped_strings)
                text = re.sub('[\r\n]+', '\r\n\r\n', text)
                file.write(text)
                text_files.append(file_name)
            # end with
        # end for
    # end for
    logger.warn('Created: %d text files', len(text_files))
    return text_files
# end def
