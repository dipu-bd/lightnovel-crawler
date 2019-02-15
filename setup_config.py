from os import path

_here = path.abspath(path.dirname(__file__))

package_name = 'lightnovel-crawler'

short_description = 'Crawls light novels and make html, text, epub, mobi, pdf and docx'

package_keywords = 'lightnovel crawler lncrawl ebook kindle download novel'

# Get the long description from the README file
with open(path.join(_here, 'README.pip')) as f:
    long_description = f.read()

# Get the long description from the README file
with open(path.join(_here, 'requirements.txt')) as f:
    install_requires = f.readlines()
    # install_requires += ['lightnovel-crawler']

with open(path.join(_here, 'VERSION')) as f:
    current_version = f.read().strip()

package_data = {
    'lncrawl': [
        '../LICENSE',
        '../VERSION',
        '../README.md',
        'assets/html_style.css',
    ],
}

entry_points = {
    'console_scripts': [
        'lncrawl=lncrawl:main',
        'lightnovel-crawler=lncrawl:main',
    ],
}
