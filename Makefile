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
	poetry shell -n

setup ::
	$(PIP) install --user -U poetry
	poetry install

requirements ::
	poetry lock
	@poetry export -f requirements.txt -o requirements.txt
	@poetry export --dev -f requirements.txt -o requirements-dev.txt

lint ::
	@echo "Stop the build if there are Python syntax errors or undefined names"
	poetry run flake8 --count --ignore="E501" --statistics lncrawl tests 
	@echo "exit-zero treats all errors as warnings."
	poetry run flake8 --count  --exit-zero --max-complexity=10 --max-line-length=120 --statistics lncrawl tests 

format ::
	@echo "Automatic reformatting"
	poetry run autopep8 -aaa --in-place --max-line-length=80 --recursive lncrawl tests

clean ::
	@echo "--- Cleaning auto-generated files ---"
	@make clean_pycache
	@$(DEL) report.xml coverage.xml
	@$(RMDIR) build dist .tox .egg lightnovel_crawler.egg-info


ifeq ($(OS),Windows_NT)
clean_pycache ::
	@$(RMDIR) $(shell dir "." /AD /B /S | findstr /E /I /R "__pycache__")
else
clean_pycache ::
	@$(RMDIR) $(shell find "." -type d -name "__pycache__")
endif

test ::
	@echo "--- Running all tests ---"
	poetry run tox --parallel auto

watch ::
	@echo "--- Select recent changes and re-run tests ---"
	poetry run ptw -- --testmon

retry ::
	@echo "--- Retry failed tests on every file change ---"
	poetry run py.test -n auto --forked --looponfail

ci ::
	@echo "--- Generate a test report ---"
	poetry run py.test -n 8 --forked --junitxml=report.xml

coverage ::
	@echo "--- Generate a test coverage ---"
	poetry run py.test --cov-config=.coveragerc --verbose --cov-report=term --cov-report=xml --cov=lncrawl tests
	poetry run coveralls

build ::
	@make clean lint
	$(PYTHON) setup.py sdist bdist_wheel --universal

publish ::
	@make build
	$(PIP) install 'twine>=1.5.0'
	twine upload dist/*
	@make clean

publish_test ::
	@make build
	$(PIP) install 'twine>=1.5.0'
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@make clean

run ::
	@poetry run mypy .
