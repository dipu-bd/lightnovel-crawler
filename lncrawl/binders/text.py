# -*- coding: utf-8 -*-
import logging
import os
import re

from bs4 import BeautifulSoup

from ..assets.icons import Icons

logger = logging.getLogger(__name__)


def make_texts(app, data):
    text_files = []
    for vol in data:
        dir_name = os.path.join(app.output_path, 'text', vol)
        os.makedirs(dir_name, exist_ok=True)
        for chap in data[vol]:
            file_name = '%s.txt' % str(chap['id']).rjust(5, '0')
            file_name = os.path.join(dir_name, file_name)
            with open(file_name, 'w', encoding='utf8') as file:
                body = chap['body'].replace('</p><p', '</p>\n<p')
                soup = BeautifulSoup(body, 'lxml')
                text = '\n\n'.join(soup.stripped_strings)
                text = re.sub(r'[\r\n]+', Icons.EOL + Icons.EOL, text)
                file.write(text)
                text_files.append(file_name)
            # end with
        # end for
    # end for
    print('Created: %d text files' % len(text_files))
    return text_files
# end def
