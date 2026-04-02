from __future__ import annotations

from functools import cached_property
from typing import Any, Dict, List, Optional, Union

import lxml.etree as etree
from bs4 import BeautifulSoup, Tag
from requests import Response


class PageSoup:
    """Safe wrapper around BeautifulSoup Tag for convenient element operations.

    All selection methods return PageSoup instances, never None.
    All text/HTML extraction methods return str, never None.
    An empty PageSoup (wrapping no tag) is falsy and returns safe defaults.

    For advanced BeautifulSoup operations not covered by this wrapper,
    access the underlying Tag via the `.tag` property.
    """

    def __init__(self, tag: Optional[Tag] = None):
        self._tag = tag if isinstance(tag, Tag) else None

    def __bool__(self) -> bool:
        return self._tag is not None

    def __repr__(self) -> str:
        if not self._tag:
            return "PageSoup(empty)"
        return f"PageSoup(<{self._tag.name}>)"

    def __str__(self) -> str:
        return self.outer_html

    def __len__(self) -> int:
        if not self._tag:
            return 0
        return sum(1 for c in self._tag.children if isinstance(c, Tag))

    def __iter__(self):
        return iter(self.children)

    def __contains__(self, selector: str) -> bool:
        """Check if a CSS selector matches any element: `if '.class' in element:`"""
        return bool(self.select_one(selector))

    def __getattr__(self, name: str):
        """Delegate unknown attribute access to the underlying Tag for backward compatibility."""
        try:
            tag = object.__getattribute__(self, "_tag")
        except AttributeError:
            return None
        if tag is not None:
            return getattr(tag, name, None)
        return None

    def __getitem__(self, key: str) -> str:
        return self.get_attr(key)

    # ------------------------------------------------------------------ #
    # Class methods
    # ------------------------------------------------------------------ #

    @classmethod
    def create(
        cls,
        data: Union[Response, bytes, str, Any],
        encoding: Optional[str] = None,
        parser: Optional[str] = None,
    ) -> "PageSoup":
        """
        Create an PageSoup from the given data.

        Args:
        - data (Union[Response, bytes, str, Any]): The data to create an PageSoup from.
        - encoding (Optional[str]): The encoding of the data.
        - parser (Optional[str]): Desirable features of the parser to be used.
          This may be the name of a specific parser ("lxml", "lxml-xml", "html.parser", or "html5lib")
          or it may be the type of markup to be used ("html", "html5", "xml"). It's recommended that
          you name a specific parser, so that Beautiful Soup gives you the same results across platforms
          and virtual environments. Default: "lxml".
        """
        if isinstance(data, Response):
            return cls.create(data.content, encoding)
        elif isinstance(data, bytes):
            html = data.decode(encoding or "utf8", "ignore")
        elif isinstance(data, str):
            html = data
        else:
            raise ValueError("Invalid data type")
        try:
            soup = BeautifulSoup(html, features=parser or "lxml")
        except Exception as e:
            raise ValueError("Failed to parse data") from e
        return cls(soup)

    # ------------------------------------------------------------------ #
    # Selection
    # ------------------------------------------------------------------ #

    @property
    def tag(self) -> Optional[Tag]:
        """Access the underlying Tag directly."""
        return self._tag

    def select(self, selector: str, limit: int = 0) -> List["PageSoup"]:
        """Select all elements matching a CSS selector.

        If limit is 0, all elements are returned.
        """
        if not self._tag:
            return []
        try:
            return [
                PageSoup(t) for t in self._tag.select(selector, limit=limit) if isinstance(t, Tag)
            ]
        except Exception:
            return []

    def select_one(self, selector: str) -> "PageSoup":
        """Select the first element matching a CSS selector.

        Returns an empty (falsy) PageSoup when nothing matches,
        so chained access like `element.select_one('.title').text` is always safe.
        """
        try:
            if self._tag:
                result = self._tag.select_one(selector)
                if isinstance(result, Tag):
                    return PageSoup(result)
        except Exception:
            pass
        return PageSoup()

    def parents(self, selector: str = "") -> List["PageSoup"]:
        """Yield ancestor elements, optionally filtered by a CSS selector.

        Walks up the tree from the parent (excludes self).
        Without a selector, yields all ancestors.
        """
        if not self._tag:
            return []
        parents = []
        try:
            node = self._tag.parent
            while isinstance(node, Tag):
                if not selector or node.css.match(selector):
                    parents.append(PageSoup(node))
                node = node.parent
        except Exception:
            pass
        return parents

    def closest(self, selector: str) -> "PageSoup":
        """Find the nearest ancestor (or self) matching a CSS selector.

        Walks up the tree starting from this element. Returns an empty
        PageSoup if no ancestor matches.
        """
        try:
            if self._tag:
                result = self._tag.css.closest(selector)
                if isinstance(result, Tag):
                    return PageSoup(result)
        except Exception:
            pass
        return PageSoup()

    def find(
        self,
        name=None,
        attrs={},
        recursive=True,
        string=None,
        **kwargs,
    ) -> "PageSoup":
        """Find the first matching element. Returns empty PageSoup if not found."""
        try:
            if self._tag:
                result = self._tag.find(name, attrs, recursive, string, **kwargs)
                if isinstance(result, Tag):
                    return PageSoup(result)
        except Exception:
            pass
        return PageSoup()

    def find_all(
        self,
        name=None,
        attrs={},
        recursive=True,
        string=None,
        limit=None,
        **kwargs,
    ) -> List["PageSoup"]:
        """Find all matching elements."""
        if not self._tag:
            return []
        try:
            return [
                PageSoup(t)
                for t in self._tag.find_all(name, attrs, recursive, string, limit, **kwargs)
                if isinstance(t, Tag)
            ]
        except Exception:
            return []

    def xpath(self, expression: str) -> List["PageSoup"]:
        """Select elements using an XPath expression.

        Parses the element's HTML with lxml, runs the XPath query,
        and converts matched elements back to PageSoup wrappers.

        XPath expressions that return strings (e.g. `//a/@href` or `//p/text()`)
        are ignored — use `select` + attribute/text access instead.
        """
        soups = []
        try:
            if not self._tag:
                return []
            doc = etree.HTML(str(self._tag))
            elements = doc.xpath(expression)
            if not isinstance(elements, list):
                return []
            for el in elements:
                if not isinstance(el, etree._Element):
                    continue
                html = etree.tostring(el, encoding="unicode", method="html")
                soup = BeautifulSoup(html, "lxml")
                soups.append(PageSoup(soup.find("body")))
        except Exception:
            pass
        return soups

    # ------------------------------------------------------------------ #
    # Text extraction
    # ------------------------------------------------------------------ #

    @property
    def text(self) -> str:
        """Stripped text content. Always returns a string, never None."""
        return self.get_text(strip=True)

    def get_text(self, separator: str = "", strip: bool = True) -> str:
        """Text content with configurable separator and stripping."""
        try:
            if self._tag:
                return self._tag.get_text(separator=separator, strip=strip)
        except Exception:
            pass
        return ""

    # ------------------------------------------------------------------ #
    # HTML extraction
    # ------------------------------------------------------------------ #

    @property
    def inner_html(self) -> str:
        """Inner HTML content (children only, excluding the tag itself)."""
        try:
            if self._tag:
                return self._tag.decode_contents()
        except Exception:
            pass
        return ""

    @property
    def outer_html(self) -> str:
        """Outer HTML (the tag and all its children)."""
        try:
            if self._tag:
                return str(self._tag)
        except Exception:
            pass
        return ""

    # ------------------------------------------------------------------ #
    # Tag information
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        """Tag name (e.g. ``'div'``, ``'a'``). Empty string for empty elements."""
        if not self._tag:
            return ""
        return self._tag.name or ""

    @property
    def string(self) -> str:
        """Direct text child of this tag, or empty string."""
        if not self._tag:
            return ""
        return str(self._tag.string or "")

    # ------------------------------------------------------------------ #
    # Attribute access
    # ------------------------------------------------------------------ #

    @property
    def attrs(self) -> Dict[str, Any]:
        """All attributes as a dictionary."""
        if not self._tag:
            return {}
        return dict(self._tag.attrs)

    @attrs.setter
    def attrs(self, attrs: Dict[str, Any]):
        """Set all attributes as a dictionary."""
        if self._tag:
            self._tag.attrs = attrs

    def has_attr(self, key: str) -> bool:
        """Check whether an attribute exists on this element."""
        if not self._tag:
            return False
        return self._tag.has_attr(key)

    def get_attr(self, key: str, default: str = "") -> str:
        """Get an attribute value, falling back to *default*."""
        if not self._tag:
            return default
        try:
            if self._tag:
                val = self._tag.get(key)
                if isinstance(val, list):
                    return " ".join(str(v) for v in val)
                if val is not None:
                    return str(val)
        except Exception:
            pass
        return default

    def get(self, key: str, default: str = "") -> str:
        """Get an attribute value, falling back to *default*."""
        return self.get_attr(key, default)

    # ------------------------------------------------------------------ #
    # Tree navigation
    # ------------------------------------------------------------------ #

    @property
    def next_sibling(self) -> "PageSoup":
        """Next sibling *element* (skips text nodes)."""
        if not self._tag:
            return PageSoup()
        node = self._tag.next_sibling
        while node and not isinstance(node, Tag):
            node = node.next_sibling
        return PageSoup(node) if isinstance(node, Tag) else PageSoup()

    @property
    def previous_sibling(self) -> "PageSoup":
        """Previous sibling *element* (skips text nodes)."""
        if not self._tag:
            return PageSoup()
        node = self._tag.previous_sibling
        while node and not isinstance(node, Tag):
            node = node.previous_sibling
        return PageSoup(node) if isinstance(node, Tag) else PageSoup()

    @property
    def parent(self) -> "PageSoup":
        """Parent element."""
        if not self._tag or not self._tag.parent:
            return PageSoup()
        p = self._tag.parent
        if isinstance(p, Tag):
            return PageSoup(p)
        return PageSoup()

    @property
    def children(self) -> List["PageSoup"]:
        """Direct child elements (excludes text nodes)."""
        if not self._tag:
            return []
        return [PageSoup(c) for c in self._tag.children if isinstance(c, Tag)]

    @property
    def contents(self) -> List[Union["PageSoup", str]]:
        """All direct children including text nodes, as a raw list."""
        if not self._tag:
            return []
        return [PageSoup(c) if isinstance(c, Tag) else str(c) for c in self._tag.contents]

    # ------------------------------------------------------------------ #
    # Mutation
    # ------------------------------------------------------------------ #

    @cached_property
    def root(self) -> Optional[BeautifulSoup]:
        """Access the underlying BeautifulSoup directly."""
        if not self._tag:
            return None
        if isinstance(self._tag, BeautifulSoup):
            return self._tag
        parents = list(self._tag.parents)
        if not parents:
            return None
        root = parents[-1]
        if isinstance(root, BeautifulSoup):
            return root
        return None

    @property
    def body(self) -> "PageSoup":
        """Get the body tag."""
        if self.root:
            return PageSoup(self.root.find("body"))
        return PageSoup()

    def decompose(self, selector: Optional[str] = None) -> "PageSoup":
        """Decompose elements matching the selector."""
        if not self._tag:
            return self
        try:
            if selector is not None:
                for t in self._tag.select(selector):
                    if isinstance(t, Tag):
                        t.decompose()
            else:
                self._tag.decompose()
        except Exception:
            pass
        return self

    def extract(self) -> "PageSoup":
        """Remove this element from the tree and return it."""
        return self.decompose()

    def new_tag(
        self,
        name: str,
        namespace: Optional[str] = None,
        nsprefix: Optional[str] = None,
        attrs: Optional[Dict[str, str]] = None,
        sourceline: Optional[int] = None,
        sourcepos: Optional[int] = None,
        string: Optional[str] = None,
        **kwargs: Any,
    ) -> "PageSoup":
        if not self.root:
            raise ValueError("Cannot create a new tag on an empty soup")
        tag = self.root.new_tag(
            name,
            namespace,
            nsprefix,
            attrs,
            sourceline,
            sourcepos,
            string,
            **kwargs,
        )
        return PageSoup(tag)

    def append(self, tag: Union[str, "PageSoup"]) -> None:
        if not self._tag:
            return
        if isinstance(tag, str):
            self._tag.append(tag)
        elif isinstance(tag, PageSoup) and tag._tag:
            self._tag.append(tag._tag)

    def replace_with(self, *tags: Union[str, "PageSoup"]) -> "PageSoup":
        if not self._tag:
            return self
        contents: List[Union[str, Tag]] = []
        for t in tags:
            if isinstance(t, str):
                contents.append(t)
            elif isinstance(t, PageSoup) and t._tag:
                contents.append(t._tag)
        self._tag.replace_with(*contents)
        return self
