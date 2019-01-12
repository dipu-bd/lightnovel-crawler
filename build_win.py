import os
import sys
import shlex
import shutil
from PyInstaller import __main__ as pyi

dir_name = os.path.abspath(os.path.dirname(__file__))
output = os.path.join(dir_name, 'windows')

additional_files = {
    'VERSION': '.',
    'LICENSE': '.',
    'lightnovel_crawler/assets/html_style.css': 'lightnovel_crawler/assets/',
}

def setup_command():
    cur_dir = '/'.join(dir_name.split(os.sep))

    command = 'pyinstaller -y '
    command += '-n "lncrawl" '
    command += '-F ' # onefile
    command += '-i "%s/lncrawl.ico" ' % cur_dir

    for k, v in additional_files.items():
        command += '--add-data "%s/%s";"%s" ' % (cur_dir, k, v)
    # end for

    command += '"%s/__main__.py" ' % cur_dir
    
    extra = ['--distpath', os.path.join(dir_name, 'dist')]
    extra += ['--workpath', os.path.join(output, 'build')]
    extra += ['--specpath', output]

    sys.argv = shlex.split(command) + extra
# end def


def main():
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)
    setup_command()
    pyi.run()
    shutil.rmtree(output, ignore_errors=True)
# end def


if __name__ == '__main__':
    main()
# end if
