import os
import sys

cur_dir = os.path.dirname(__file__)

module_list = [
    'lightnovel_crawler.assets.version',
    'lightnovel_crawler.assets.html_style',
]

full_path = {
    x: x.replace('.', os.path.sep) + '.py'
    for x in module_list
}

backups = dict()
for item in module_list:
    __import__(item)
    with open(full_path[item], 'r') as f:
        backups[item] = f.read()

def pack_files():   
    fmt = "def get_value():\n    return '''%s'''\n"
    for item in module_list:
        mod = sys.modules[item] 
        value = mod.get_value()
        with open(full_path[item], 'w') as f:
            f.write(fmt % value)

def unpack_files():
    for item in module_list:
        with open(full_path[item], 'w') as f:
            f.write(backups[item])

if __name__ == '__main__':
    input('Press Enter to build assets...')
    pack_files()
    input('Press Enter to reset assets...')
    unpack_files()
# end if
