VERSION=$(head -n 1 VERSION)

rm -r build dist *.egg-info

python setup.py bdist_wheel sdist
python setup_win.py

twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"
