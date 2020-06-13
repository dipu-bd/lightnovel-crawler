#!/usr/bin/env python
import sys
import os.path
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 5):
    raise RuntimeError(
        'Lightnovel crawler only supports Python 3.5 and later.')
else:
    run_pyi = 'package' in sys.argv
    if run_pyi:
        sys.argv.remove('package')
    # end if
    if len(sys.argv) == 1:
        sys.argv += ['build']
    # end if

    # import required packages
    from pathlib import Path
    from setuptools import config, setup

    def parse_version(filename):
        with open(filename, 'r') as f:
            return f.read().strip()
    # end def

    def parse_requirements(filename):
        """Return requirements from requirements file."""
        # Ref: https://stackoverflow.com/a/42033122/
        requirements = open(filename, 'r').read().strip().split('\n')
        requirements = [r.strip() for r in requirements]
        requirements = [r for r in sorted(
            requirements) if r and not r.startswith('#')]
        return requirements
    # end def

    config.read_configuration('setup.cfg')
    setup(
        name="lncrawl",
        version=parse_version(os.path.join('lncrawl', 'VERSION')),
        packages=find_packages(),
        install_requires=parse_requirements('requirements.txt'),
        # metadata to display on PyPI
        author="dipu-bd",
        description="An app to download novels from online sources and generate e-books.",
        keywords="lightnovel epub scraper web-scraper lncrawl",
        url="https://github.com/dipu-bd/lightnovel-crawler",
        project_urls={
            "Bug Tracker": "https://github.com/dipu-bd/lightnovel-crawler/issues",
            "Documentation": "https://github.com/dipu-bd/lightnovel-crawler/blob/master/README.md",
            "Source Code": "https://github.com/dipu-bd/lightnovel-crawler",
        },
    )

    if run_pyi:
        from setup_pyi import package
        package()
    # end if
# end if
