

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@poetry env info


.PHONY: fmt
fmt: .venv             ## Format code using black & isort.
	$(ENV_PREFIX)isort $(PROJECT_NAME)/
	$(ENV_PREFIX)black $(PROJECT_NAME)/
	$(ENV_PREFIX)black tests/

.PHONY: lint
lint: .venv             ## Run pep8, black, mypy linters.
	$(ENV_PREFIX)pylint $(PROJECT_NAME)/
	$(ENV_PREFIX)black --check $(PROJECT_NAME)/
	$(ENV_PREFIX)black --check tests/
	$(ENV_PREFIX)mypy --ignore-missing-imports $(PROJECT_NAME)/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v --cov-config .coveragerc --cov=$(PROJECT_NAME) -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: clean
clean:            ## Clean unused files.
	find ./ -name '*.pyc' -exec rm -f {} \;
	find ./ -name '__pycache__' -exec rm -rf {} \;
	find ./ -name 'Thumbs.db' -exec rm -f {} \;
	find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build

.PHONY: clean-venv
clean-venv: 	## Remove the installed viertual environment
	rm -r .venv

.venv:       ## Create a virtual environment.
	export POETRY_VIRTUALENVS_IN_PROJECT=true && \
	poetry install

.PHONY: pre-commit-install
pre-commit-install: .git/hooks/pre-commit
.git/hooks/pre-commit: .venv
	$(ENV_PREFIX)pre-commit install

.PHONY: pre-commit
pre-commit: pre-commit-install
	$(ENV_PREFIX)pre-commit run --all-files


.PHONY: git-tag
git-tag:	## Create new Git tag
	git tag -a "v$(VERSION)" -m ""
	git push origin "v$(VERSION)"


POETRY_VERSION_CMD=poetry version
.PHONY: bump-major
bump-major:
	$(POETRY_VERSION_CMD) major

.PHONY: bump-minor
bump-minor:
	$(POETRY_VERSION_CMD) minor

.PHONY: bump-patch
bump-patch:
	$(POETRY_VERSION_CMD) patch

