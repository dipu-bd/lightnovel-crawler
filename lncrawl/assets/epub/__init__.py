from pathlib import Path

from css_html_js_minify import css_minify

ROOT = Path(__file__).parent

with open(str(ROOT / "style.css"), "r", encoding="utf8") as f:
    style = css_minify(f.read())


def get_css_style():
    return style
