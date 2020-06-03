#!/usr/bin/env python
import os
import sys

from src import VERSION

cur_dir = os.path.dirname(__file__)


def long_description():
    filename = os.path.join(cur_dir, 'README.md')
    with open(filename, 'r') as f:
        return f.read()


def read_requirements(filename):
    # Ref: https://stackoverflow.com/a/42033122/
    with open(filename, 'r') as f:
        requirements = [r.strip() for r in f.readlines()]
        requirements = [r for r in requirements
                        if r and not r.startswith('#')]
        return requirements


def run_setup():
    # import required packages
    from setuptools import setup, find_packages

    # configure setup
    setup(
        name='lightnovel-crawler',
        author='Sudipto Chandra',
        author_email='dipu.sudipta@gmail.com',
        description='Crawls light novels and make html, text, epub, mobi, pdf and docx',
        long_description=long_description(),
        long_description_content_type='text/markdown',
        license='Apache 2.0',
        license_file='LICENSE',

        version=VERSION,
        install_requires=read_requirements(
            os.path.join(cur_dir, 'requirements-pip.txt')),
        tests_require=read_requirements(
            os.path.join(cur_dir, 'requirements-dev.txt')),
        packages=find_packages(),
        package_dir={'lnc': 'src'},
        include_package_data=True,

        entry_points={
            'console_scripts': [
                'lnc = src:main',
                'lncrawl = src:main',
                'lightnovel-crawler = src:main',
            ],
        },

        url='https://github.com/dipu-bd/lightnovel-crawler',
        project_urls={
            'Code':  'https://github.com/dipu-bd/lightnovel-crawler',
            'Issue tracker':  'https://github.com/dipu-bd/lightnovel-crawler/issues',
            'Documentation':  'https://github.com/dipu-bd/lightnovel-crawler/blob/master/README.md',
        },

        platforms=[
            'Linux',
            'MacOS',
            'Windows',
        ],
        keywords=[
            'lightnovel',
            'crawler',
            'lncrawl',
            'download',
            'ebook',
            'novel',
            'pdf',
            'epub',
            'mobi',
            'kindle',
        ],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop  ',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Games/Entertainment',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Multimedia :: Graphics',
            'Topic :: Printing',
            'Topic :: Text Processing :: Markup :: HTML',
        ],
    )


if sys.version_info[:2] < (3, 5):
    raise RuntimeError("Lightnovel-Crawler only supports python >= 3.5")


run_pyi = 'package' in sys.argv
if run_pyi:
    sys.argv.remove('package')

run_setup()

if run_pyi:
    from setup_pyi import package
    package()
