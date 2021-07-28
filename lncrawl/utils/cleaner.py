# -*- coding: utf-8 -*-
"""
NOTE: DEPRECATED. use self.clean_text instead
"""

# import re
# import sys
# import itertools
# import functools
# import unicodedata

# ALL_CHARS = (i for i in range(sys.maxunicode))
# INVISIBLE_CHARS = [c for c in ALL_CHARS if unicodedata.category(chr(c)) in {'Cf', 'Cc'}]
# # Use characters of control category
# NONPRINTABLE = itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0), INVISIBLE_CHARS)
# transliterable = {character: None for character in NONPRINTABLE}


# def _strip_nonprintable_characters(text):
#     # Use translate to remove all non-printable characters
#     return text.translate(transliterable)


# def _get_shortest_match(regex, content):
#     regex = f"(?=({regex}))"
#     matches = re.findall(regex, content)
#     if matches:
#         shortest = min(matches, key=len)
#         # prevents issues if capturing group was used instead of non-capturing
#         # as capturing group will return tuple instead of string, that can't
#         # be passed to re.sub later
#         if type(shortest) == tuple:
#             shortest = shortest[0]
#         return shortest
#     return ""


# def _clean_contents(content: str):
#     blacklist_patterns = [
#         r'<p>\s*Chapter \d+[^<]+</p>',
#         r'<h[1-6]>\s*Chapter \d+[^<]+</h[1-6]>',
#         # r'<p>\s*(Translator|Translated)[^<]{2,30}</p>',
#         r'<p>\s*(Editor|Edited)[^<]*</p>',
#         r'<p>\s*Exodus Tales[^<]*</p>',     # blacklist Exodus tales "ad"
#         r'Read more chapter on NovelFull',  # strip "ads"
#         r'full thich ung',      # leftover from previous blacklist
#         r'<p><i>\d</i></p>',    # strip random numbers
#         r'<p>\s*</p>',  # strip any empty paragraphs
#     ]

#     substitute = {
#         'u003c': '<',
#         'u003e': '>',
#         '"s': "'s",
#         '“s': "'s",
#         '”s': "'s",
#     }

#     content = _strip_nonprintable_characters(content)

#     for pattern in blacklist_patterns:
#         content = re.sub(pattern, '', content)

#     for pattern, substitution in substitute.items():
#         content = re.sub(pattern, substitution, content)

#     return content

# def cleanup_text(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         text = func(*args, **kwargs)
#         text = _clean_contents(text)
#         return text
#     return wrapper
