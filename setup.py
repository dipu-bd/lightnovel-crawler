#!/usr/bin/env python
import sys
import os.path

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
        version=parse_version(os.path.join('src', 'VERSION')),
        install_requires=parse_requirements('requirements.txt'),
    )

    if run_pyi:
        from setup_pyi import package
        package()
    # end if
# end if
