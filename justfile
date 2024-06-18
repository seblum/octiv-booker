# Show the help
help:
    @echo "Usage: just <target>"
    @echo ""
    @echo "Targets:"
    @grep "##" justfile | grep -v grep

# Show the current environment
show: ##
    @echo "Current environment:"
    @poetry env info

# Format code using black & isort
fmt: 
    {{env_prefix()}}isort {{project_name()}}/
    {{env_prefix()}}black {{project_name()}}/
    {{env_prefix()}}black tests/

# Run pep8, black, mypy linters
lint: 
    {{env_prefix()}}pylint {{project_name()}}/
    {{env_prefix()}}black --check {{project_name()}}/
    {{env_prefix()}}black --check tests/
    {{env_prefix()}}mypy --ignore-missing-imports {{project_name()}}/

# Run tests and generate coverage report
test: lint ## 
    {{env_prefix()}}pytest -v --cov-config .coveragerc --cov={{project_name()}} -l --tb=short --maxfail=1 tests/
    {{env_prefix()}}coverage xml
    {{env_prefix()}}coverage html

# Clean unused files
clean: ##
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

# Remove the installed virtual environment
clean-venv: ## 
    rm -r .venv

# Create a virtual environment
venv:
    export POETRY_VIRTUALENVS_IN_PROJECT=true && \
    poetry install

# Install pre-commit hooks
pre-commit: 
    pre-commit install
    
# Run pre-commit hooks
pre-commit: pre-commit-install
    {{env_prefix()}}pre-commit run --all-files

# Create new Git tag
git-tag: ## 
    git tag -a "v{{version()}}" -m ""
    git push origin "v{{version()}}"

# Bump major version
bump-major:
    poetry version major

# Bump minor version
bump-minor:
    poetry version minor

# Bump patch version
bump-patch:
    poetry version patch

# Utility functions
env_prefix = @($(ENV_PREFIX))
project_name = $(PROJECT_NAME)
version = $(VERSION)
