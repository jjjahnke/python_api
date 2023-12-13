# Variables
VENV           = .venv
VENV_PYTHON    = $(VENV)/bin/python
SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON         = $(or $(wildcard $(VENV_PYTHON)), $(SYSTEM_PYTHON))
ACTIVATE	   = $(VENV)/bin/activate

## Dev/build environment

$(VENV_PYTHON):
	rm -rf $(VENV)
	$(SYSTEM_PYTHON) -m venv $(VENV)

$(VENV)/install.stamp: $(VENV_PYTHON) requirements.txt requirements-dev.txt
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install --upgrade -r requirements-dev.txt
	$(VENV_PYTHON) -m pip install --upgrade -r requirements.txt
	touch $(VENV)/install.stamp

PHONY: venv
venv: $(VENV_PYTHON)

PHONY: deps
deps: $(VENV)/install.stamp

help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  venv      - Create virtual environment"
	@echo "  deps      - Install dependencies"
	@echo "  test      - Run tests"
	@echo "  clean     - Clean up"

## Test

lint: deps
	$(VENV_PYTHON) -m black src/
	$(VENV_PYTHON) -m flake8 --statistics src/

test: deps
	docker-compose -f test-env-compose.yaml down
	docker-compose -f test-env-compose.yaml up -d
	$(VENV_PYTHON) -m pytest -svv --basetemp=/tmp/pytest --cov=src --cov-report=term-missing --cov-report=json tests/

## Build source distribution, install
build: deps
	docker build -t docker.io/$(DOCKER_USERNAME)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .

## Clean

clean:
	$(VENV_PYTHON) -m pip cache purge
	rm -rf $(VENV)
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -rf htmlcov
	find . -name '\.coverage*' -delete
	rm -rf .pytest_cache