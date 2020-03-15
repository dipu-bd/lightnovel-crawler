# Default task: init

init:
	pip install -r requirements.txt
	pip install wheel

test:
	# This runs all of the tests.
	tox --parallel auto

watch:
	# This automatically selects and re-executes only tests affected by recent changes.
	ptw -- --testmon

retry:
	# This will retry failed tests on every file change.
	py.test -n auto --forked --looponfail

ci:
	py.test -n 8 --forked --junitxml=report.xml

lint:
	# Stop the build if there are Python syntax errors or undefined names
	flake8 --count --ignore="E501" --statistics src tests 
	# exit-zero treats all errors as warnings.
	flake8 --count  --exit-zero --max-complexity=10 --max-line-length=120 --statistics src tests 

format:
	# Automatic reformatting
	autopep8 -aaa --in-place --max-line-length=80 --recursive src tests

coverage:
	py.test --cov-config=.coveragerc --verbose --cov-report=term --cov-report=xml --cov=src tests
	coveralls

clean:
	rm -rfv build dist .egg src.egg-info report.xml coverage.xml
	rm -rfv **/__pycache__

build:
	make clean
	make lint
	python3 setup.py sdist bdist_wheel --universal

install:
	pip3 uninstall -y lightnovel-crawler
	python3 setup.py install

publish:
	make build
	pip3 install 'twine>=1.5.0'
	twine upload dist/*
	make clean

publish_test:
	make build
	pip3 install 'twine>=1.5.0'
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	make clean
