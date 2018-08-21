VERSION=$(head -n 1 VERSION)

python setup.py bdist_wheel
python setup.py sdist
twine upload "dist/ebook_crawler-$VERSION-py3-none-any.whl"
