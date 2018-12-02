import os

cur_dir = os.path.dirname(__file__)

from .version import get_value as version
with open(os.path.join(cur_dir, 'version.py'), 'r') as f:
    version_ = f.read()
    
from .html_style import get_value as html_style
with open(os.path.join(cur_dir, 'html_style.py'), 'r') as f:
    html_style_ = f.read()

def pack_files():   
    fmt = "def get_value():\n    return '''%s'''\n"
    with open(os.path.join(cur_dir, 'version.py'), 'w') as f:
        f.write(fmt % version())
    with open(os.path.join(cur_dir, 'html_style.py'), 'w') as f:
        f.write(fmt % html_style())


def unpack_files():
    with open(os.path.join(cur_dir, 'version.py'), 'w') as f:
        f.write(version_)
    with open(os.path.join(cur_dir, 'html_style.py'), 'w') as f:
        f.write(html_style_)
