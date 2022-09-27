import itertools
import re
import sys
import unicodedata

from bs4 import Comment, Tag

LINE_SEP = "<br>"

INVISIBLE_CHARS = [
    c for c in range(sys.maxunicode) if unicodedata.category(chr(c)) in {"Cf", "Cc"}
]
NONPRINTABLE = itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0), INVISIBLE_CHARS)
NONPRINTABLE_MAPPING = {character: None for character in NONPRINTABLE}


class TextCleaner:
    def __init__(self) -> None:
        self.bad_text_regex = set([])
        self.bad_tags = set(
            [
                "noscript",
                "script",
                "style",
                "iframe",
                "ins",
                "header",
                "footer",
                "button",
                "input",
                "amp-auto-ads",
                "pirate",
                "figcaption",
                "address",
                "tfoot",
                "object",
                "video",
                "audio",
                "source",
                "nav",
                "output",
                "select",
                "textarea",
                "form",
                "map",
            ]
        )
        self.bad_css = set(
            [
                ".code-block",
                ".adsbygoogle",
                ".sharedaddy",
                ".inline-ad-slot",
                ".ads-middle",
                ".jp-relatedposts",
                ".ezoic-adpicker-ad",
                ".ezoic-ad-adaptive",
                ".ezoic-ad",
                ".cb_p6_patreon_button",
                ".adbox",
                ".googlepublisherads",
                ".adblock-service",
                ".adsense-code"
                'a[href*="paypal.me"]',
                'a[href*="patreon.com"]',
            ]
        )
        self.p_block_tags = set(
            [
                "p",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "main",
                "aside",
                "article",
                "div",
                "section",
            ]
        )
        self.unchanged_tags = set(["pre", "canvas", "img"])
        self.plain_text_tags = set(
            [
                "span",
                "a",
                "abbr",
                "acronym",
                "label",
                "time",
            ]
        )
        self.substitutions = {
            '"s': "'s",
            "“s": "'s",
            "”s": "'s",
            "&": "&amp;",
            "u003c": "<",
            "u003e": ">",
            "<": "&lt;",
            ">": "&gt;",
        }
        self.whitelist_attributes = set(
            [
                "src",
                "style",
            ]
        )
        self.whitelist_css_property = set(
            [
                "font-weight",
                "font-style",
            ]
        )

    def extract_contents(self, tag) -> str:
        self.clean_contents(tag)
        body = " ".join(self.extract_paragraphs(tag))
        # body = self.remove_bad_texts(body)

        return "".join(
            [f"<p>{x.strip()}</p>" for x in body.split(LINE_SEP) if x.strip()]
        )

    def clean_contents(self, div):
        if not isinstance(div, Tag):
            return div

        if self.bad_css:
            for bad in div.select(",".join(self.bad_css)):
                bad.extract()

        for tag in div.find_all(True):
            if isinstance(tag, Comment):
                tag.extract()  # Remove comments
            elif not isinstance(tag, Tag):
                continue  # Skip elements that are not a Tag
            if tag.name in self.bad_tags:
                tag.extract()  # Remove bad tags
            elif tag.name in ["br", "hr"]:
                self.extract_on_duplicate_sibling(tag)
            else:
                self.clean_attributes(tag)

        self.clean_attributes(div)
        return div

    def clean_text(self, text) -> str:
        text = str(text).strip()
        text = text.translate(NONPRINTABLE_MAPPING)
        for k, v in self.substitutions.items():
            text = text.replace(k, v)
        return self.remove_bad_texts(text)

    def extract_on_duplicate_sibling(self, tag: Tag):
        next_tag = tag.next_sibling
        if not isinstance(next_tag, Tag):
            return
        if next_tag.name == tag.name:
            tag.extract()

    def clean_attributes(self, tag: Tag) -> dict:
        attrs = {}
        for name, value in tag.attrs.items():
            if name not in self.whitelist_attributes:
                continue
            if name == "style":
                value = self.clean_style_value(value)
            if value:
                attrs[name] = value
        tag.attrs = attrs

    def clean_style_value(self, style: str) -> str:
        clean_css = []
        css = {
            item[0].strip().lower(): item[1].strip()
            for item in [x.split(":", 1) for x in style.split(";")]
            if len(item) == 2 and item[0].strip()
        }
        for name in self.whitelist_css_property:
            value = css.get(name)
            if value:
                clean_css.append(f"{name}:{value}")
        return ";".join(clean_css)

    def extract_paragraphs(self, tag) -> list:
        if not isinstance(tag, Tag):
            return []

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
            if elem.name == "hr":
                body.append(LINE_SEP)
                # body.append('-' * 8)
                # body.append(LINE_SEP)
                continue
            if elem.name == "br":
                body.append(LINE_SEP)
                continue
            # if not elem.text.strip():
            #     continue

            is_block = elem.name in self.p_block_tags
            is_plain = elem.name in self.plain_text_tags
            content = " ".join(self.extract_paragraphs(elem))

            if is_block:
                body.append(LINE_SEP)

            for line in content.split(LINE_SEP):
                line = line.strip()
                if not line:
                    continue
                if not (is_plain or is_block):
                    line = "<%s>%s</%s>" % (elem.name, line, elem.name)
                body.append(line)
                body.append(LINE_SEP)

            if body and body[-1] == LINE_SEP and not is_block:
                body.pop()

        return [x.strip() for x in body if x.strip()]

    def remove_bad_texts(self, text: str) -> str:
        if not (isinstance(text, str) and self.bad_text_regex):
            return ""
        pattern = "|".join(
            [f"({p})" for p in self.bad_text_regex if isinstance(p, str)]
        )
        return re.sub(pattern, "", text)
