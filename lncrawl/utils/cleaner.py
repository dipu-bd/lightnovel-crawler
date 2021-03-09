import re
import functools


def _get_shortest_match(regex, content):
    regex = f"(?=({regex}))"
    matches = re.findall(regex, content)
    if matches:
        shortest = min(matches, key=len)
        return shortest
    return ""


def _clean_contents(content):
    blacklist_patterns = [
        r'<p>.*?Translator.*?</p>',  # strip paragraphs with Translator
        r'<p>.*?Editor.*?</p>',  # strip paragraphs with Editor
        r'Read more chapter on NovelFull',  # strip "ads"
        r'full thich ung',  # leftover from previous blacklist
        r'<p><i>\d</i></p>',  # strip random numbers
        r'<p>[<(strong|b|i|u)>]*Chapter.*?</p>',  # strip "Chapter: ..."
        r'<p>\s*</p>',  # strip any empty paragraphs
    ]

    substitute = {
        'u003c': '<',
        'u003e': '>',
        '"s': '\'s',
        '“s': '\'s',
        '”s': '\'s',
    }

    for pattern in blacklist_patterns:
        # I used .*? when I wanted to get the shortest match, as it turns
        # out, regex doesn't work that way, for more indepth explanation
        # what goes wrong, see stackoverflow link in _get_shortest_match
        if '.*?' in pattern:
            shortest = _get_shortest_match(pattern, content)
            content = re.sub(shortest, "", content)
        else:
            content = re.sub(pattern, "", content)
        content = re.sub(pattern, "", content)

    for pattern, substitution in substitute.items():
        content = re.sub(pattern, substitution, content)

    return content


def cleanup_text(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        text = func(*args, **kwargs)
        text = _clean_contents(text)
        return text
    return wrapper
