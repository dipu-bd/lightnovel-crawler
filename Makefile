# Default task: init
ifeq ($(OS),Windows_NT)
    COPY := copy
    DEL := del
	RMDIR := rd /S /Q
	PYTHON := python
	PIP := $(PYTHON) -m pip
else
    COPY := cp
    DEL := rm -fv
	RMDIR := rm -rfv
	PYTHON := python3
	PIP := $(PYTHON) -m pip
endif


init ::
	pipenv shell --anyway

setup ::
	$(PIP) install --user -U pipenv
	pipenv install --three

lock ::
	pipenv lock
	pipenv lock -r > requirements.txt
	pipenv lock -r --dev-only > dev-requirements.txt

lint ::
	@echo "Stop the build if there are Python syntax errors or undefined names"
	pipenv run flake8 --count --ignore="E501" --statistics lncrawl tests 
	@echo "exit-zero treats all errors as warnings."
	pipenv run flake8 --count  --exit-zero --max-complexity=10 --max-line-length=120 --statistics lncrawl tests 

format ::
	@echo "Automatic reformatting"
	pipenv run autopep8 -aaa --in-place --max-line-length=80 --recursive lncrawl tests

clean ::
	@echo "--- Cleaning auto-generated files ---"
	@$(DEL) report.xml coverage.xml
	@$(RMDIR) build dist .tox .egg lightnovel_crawler.egg-info
	make clean_pycache

ifeq ($(OS),Windows_NT)
clean_pycache ::
	@for /F "delims=" %%I in ('dir "." /AD /B /S 2^>nul ^| findstr /E /I /R "__pycache__"') do @rd /Q /S "%%I" 2>nul
else
clean_pycache ::
	find . -type d -name '__pycache__' | xargs rm -rfv
endif

test ::
	@echo "--- Running all tests ---"
	pipenv run tox --parallel auto

watch ::
	@echo "--- Select recent changes and re-run tests ---"
	pipenv run ptw -- --testmon

retry ::
	@echo "--- Retry failed tests on every file change ---"
	pipenv run py.test -n auto --forked --looponfail

ci ::
	@echo "--- Generate a test report ---"
	pipenv run py.test -n 8 --forked --junitxml=report.xml

coverage ::
	@echo "--- Generate a test coverage ---"
	pipenv run py.test --cov-config=.coveragerc --verbose --cov-report=term --cov-report=xml --cov=lncrawl tests
	pipenv run coveralls

build ::
	make clean lint
	$(PYTHON) setup.py sdist bdist_wheel --universal

publish ::
	make build
	$(PIP) install 'twine>=1.5.0'
	twine upload dist/*
	make clean

publish_test ::
	make build
	$(PIP) install 'twine>=1.5.0'
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	make clean

run ::
	@pipenv run python .
