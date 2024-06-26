# Delete target on error.
# https://www.gnu.org/software/make/manual/html_node/Errors.html#Errors
# > This is almost always what you want make to do, but it is not historical
# > practice; so for compatibility, you must explicitly request it
.DELETE_ON_ERROR:

# Global tasks.
# =============================================================================
PYTHON_VERSION := python3.12
LINTER_CHECKED_DIRS := config spock tests
PGDATABASE ?= spock
REQUIREMENTS_PATH ?= requirements/dev.txt

VIRTUAL_ENV ?= .venv
export PATH := $(VIRTUAL_ENV)/bin:$(PATH)

VENV_REQUIREMENT := $(VIRTUAL_ENV)

.PHONY: runserver venv clean quality fix compile-deps

runserver: $(VIRTUAL_ENV)
	python manage.py runserver $(RUNSERVER_DOMAIN)

$(VIRTUAL_ENV): $(REQUIREMENTS_PATH)
	$(PYTHON_VERSION) -m venv $@
	$@/bin/pip install uv
	$@/bin/uv pip sync --require-hashes $^
	touch $@

venv: $(VIRTUAL_ENV)

PIP_COMPILE_FLAGS := --generate-hashes $(PIP_COMPILE_OPTIONS)
compile-deps: $(VENV_REQUIREMENT)
	uv pip compile $(PIP_COMPILE_FLAGS) -o requirements/base.txt requirements/base.in
	uv pip compile $(PIP_COMPILE_FLAGS) -o requirements/test.txt requirements/test.in
	uv pip compile $(PIP_COMPILE_FLAGS) -o requirements/dev.txt requirements/dev.in

clean:
	find . -type d -name "__pycache__" -depth -exec rm -rf '{}' \;

quality: $(VENV_REQUIREMENT)
	ruff format --check $(LINTER_CHECKED_DIRS)
	ruff check $(LINTER_CHECKED_DIRS)
	python manage.py makemigrations --check --dry-run --noinput || (echo "⚠ Missing migration ⚠"; exit 1)
	python manage.py collectstatic --no-input

fix: $(VENV_REQUIREMENT)
	ruff format $(LINTER_CHECKED_DIRS)
	ruff check --fix $(LINTER_CHECKED_DIRS)

.PHONY: test

test: $(VENV_REQUIREMENT)
	pytest --numprocesses=logical --create-db $(TARGET)

