VERSION=$(head -n 1 VERSION)

rm -rf build dist *.egg-info

python3 setup.py bdist_wheel sdist

twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"
