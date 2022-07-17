# -*- coding: utf-8 -*-
import itertools
import re
import sys
import unicodedata

from bs4 import Comment, Tag

LINE_SEP = '<br>'

INVISIBLE_CHARS = [c for c in range(sys.maxunicode) if unicodedata.category(chr(c)) in {'Cf', 'Cc'}]
NONPRINTABLE = itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0), INVISIBLE_CHARS)
NONPRINTABLE_MAPPING = {character: None for character in NONPRINTABLE}

class TextCleaner:

    def __init__(self) -> None:
        self.blacklist_patterns = set([])
        self.bad_tags = set([
            'noscript', 'script', 'style', 'iframe', 'ins', 'header', 'footer',
            'button', 'input', 'amp-auto-ads', 'pirate', 'figcaption', 'address',
            'tfoot', 'object', 'video', 'audio', 'source', 'nav', 'output', 'select',
            'textarea', 'form', 'map',
        ])
        self.bad_css = set([
            '.code-block', '.adsbygoogle', '.sharedaddy', '.inline-ad-slot', '.ads-middle',
            '.jp-relatedposts', '.ezoic-adpicker-ad', '.ezoic-ad-adaptive', '.ezoic-ad',
            '.cb_p6_patreon_button', 'a[href*="patreon.com"]', '.adbox'
        ])
        self.p_block_tags = set([
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'main', 'aside', 'article', 'div', 'section',
        ])
        self.unchanged_tags = set([
            'pre', 'canvas', 'img'
        ])
        self.plain_text_tags = set([
            'span', 'a', 'abbr', 'acronym', 'label', 'time',
        ])
        self.substitutions = {
            '"s': "'s",
            '“s': "'s",
            '”s': "'s",
            '&': '&amp;',
            'u003c': '<',
            'u003e': '>',
            '<': '&lt;',
            '>': '&gt;',
        }
    # end def

    def extract_contents(self, tag) -> str:
        self.clean_contents(tag)
        body = ' '.join(self.extract_paragraphs(tag))
        return '\n'.join([
            '<p>' + x + '</p>'
            for x in body.split(LINE_SEP)
            if not self.is_in_blacklist(x.strip())
        ])
    # end def

    def clean_contents(self, div):
        if not isinstance(div, Tag):
            return div
        # end if
        if self.bad_css:
            for bad in div.select(','.join(self.bad_css)):
                bad.extract()
            # end if
        # end if
        for tag in div.find_all(True):
            if isinstance(tag, Comment):
                tag.extract()   # Remove comments
            elif tag.name == 'br':
                next_tag = getattr(tag, 'next_sibling')
                if next_tag and getattr(next_tag, 'name') == 'br':
                    tag.extract()
                # end if
            elif tag.name in self.bad_tags:
                tag.extract()   # Remove bad tags
            elif hasattr(tag, 'attrs'):
                tag.attrs = {k: v for k, v in tag.attrs.items() if k == 'src'}
            # end if
        # end for
        div.attrs = {}
        return div
    # end def

    def clean_text(self, text) -> str:
        text = str(text).strip()
        text = text.translate(NONPRINTABLE_MAPPING)
        for k, v in self.substitutions.items():
            text = text.replace(k, v)
        # end for
        return text
    # end def

    def extract_paragraphs(self, tag) -> list:
        if not isinstance(tag, Tag):
            return []
        # end if

        body = []
        for elem in tag.contents:
            if isinstance(elem, Comment):
                continue
            if not isinstance(elem, Tag):
                body.append(self.clean_text(elem))
                continue
            if elem.name in self.unchanged_tags:
                body.append(str(elem))
                continue
            if elem.name == 'hr':
                body.append(LINE_SEP)
                # body.append('-' * 8)
                # body.append(LINE_SEP)
                continue
            if elem.name == 'br':
                body.append(LINE_SEP)
                continue
            # if not elem.text.strip():
            #     continue

            is_block = elem.name in self.p_block_tags
            is_plain = elem.name in self.plain_text_tags
            content = ' '.join(self.extract_paragraphs(elem))

            if is_block:
                body.append(LINE_SEP)
            # end if

            for line in content.split(LINE_SEP):
                line = line.strip()
                if not line:
                    continue
                # end if
                if not (is_plain or is_block):
                    line = '<%s>%s</%s>' % (elem.name, line, elem.name)
                # end if
                body.append(line)
                body.append(LINE_SEP)
            # end if

            if body and body[-1] == LINE_SEP and not is_block:
                body.pop()
            # end if
        # end for

        return [x.strip() for x in body if x.strip()]
    # end def

    def is_in_blacklist(self, text) -> bool:
        if not text:
            return True
        # end if
        if not self.blacklist_patterns:
            return False
        # end if
        pattern = getattr(self, '__blacklist__', None)
        if not pattern:
            pattern = re.compile('|'.join(['(%s)' % p for p in self.blacklist_patterns]))
            setattr(self, '__blacklist__', pattern)
        # end if
        if pattern and pattern.search(text):
            return True
        return False
    # end def
# end class
