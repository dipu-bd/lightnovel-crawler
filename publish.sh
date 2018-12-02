VERSION=$(head -n 1 lightnovel-crawler/VERSION)

git clean -xfd

python setup.py bdist_wheel
python setup.py sdist

twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"
