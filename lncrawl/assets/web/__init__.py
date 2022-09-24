from pathlib import Path

ROOT = Path(__file__).parent


def get_js_script():
    with open(str(ROOT / "script.js"), "r", encoding="utf8") as f:
        script = f.read()
    return script


def get_css_style():
    with open(str(ROOT / "style.css"), "r", encoding="utf8") as f:
        style = f.read()
    return style
