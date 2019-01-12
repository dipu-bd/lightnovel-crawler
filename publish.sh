VERSION=$(head -n 1 VERSION)

git clean -xfd

python3 setup.py bdist_wheel sdist
python3 build_win.py

twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"
