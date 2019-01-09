VERSION=$(head -n 1 VERSION)

git clean -xfd

export build_assets=true
python3 setup.py bdist_wheel sdist

twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"
