from os import path

_here = path.abspath(path.dirname(__file__))

package_name = 'lightnovel-crawler'

short_description = 'Crawls light novels and make html, text, epub and mobi'

# Get the long description from the README file
with open(path.join(_here, 'README.pip'), encoding='utf-8') as f:
    long_description = f.read()

# Get the long description from the README file
with open(path.join(_here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.readlines()
    install_requires += ['lightnovel_crawler']

with open(path.join(_here, 'VERSION'), encoding='utf-8') as f:
    current_version = f.read().strip()

package_data = {
    'lightnovel_crawler': [
        '../LICENSE',
        '../VERSION',
        '../README.md',
        'assets/html_style.css',
    ],
}

entry_points = {
    'console_scripts': [
        'lightnovel-crawler=lightnovel_crawler:main',
        'lncrawl=lightnovel_crawler:main',
    ],
}
