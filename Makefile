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
	flake8 --count --ignore="E501" --statistics lncrawl tests 
	@echo "exit-zero treats all errors as warnings."
	flake8 --count  --exit-zero --max-complexity=10 --max-line-length=120 --statistics lncrawl tests 

format ::
	@echo "Automatic reformatting"
	autopep8 -aaa --in-place --max-line-length=80 --recursive lncrawl tests

clean ::
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
	@echo "This runs all of the tests."
	tox --parallel auto

watch ::
	@echo "This automatically selects and re-executes only tests affected by recent changes."
	ptw -- --testmon

retry ::
	@echo "This will retry failed tests on every file change."
	py.test -n auto --forked --looponfail

ci ::
	py.test -n 8 --forked --junitxml=report.xml

coverage ::
	py.test --cov-config=.coveragerc --verbose --cov-report=term --cov-report=xml --cov=lncrawl tests
	coveralls

build ::
	make clean lint
	$(PYTHON) setup.py sdist bdist_wheel --universal

install ::
	$(PIP) uninstall -y lightnovel-crawler
	$(PIP) setup.py install

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
