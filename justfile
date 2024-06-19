# # Show the help
# help:
#     @echo "Usage: just <target>"
#     @echo ""
#     @echo "Targets:"
#     @grep "##" justfile | grep -v grep

# # Show the current environment
# show: ##
#     @echo "Current environment:"
#     @poetry env info


# # Remove the installed virtual environment
# clean-venv: 
#     rm -r .venv

# # Create a virtual environment
# venv:
#     export POETRY_VIRTUALENVS_IN_PROJECT=true && \
#     poetry install
#     pre-commit install

# # Run pre-commit hooks
# pre-commit:
#     pre-commit run --all-files

run:
    poetry run slotBooker

run-dev:
    poetry run slotBookerDev

# Install project dependencies using Poetry
install:
    poetry install

# Run tests using Poetry and pytest
test:
    poetry run pytest
    poetry run coverage run -m pytest
    poetry run coverage report -m

# Format code using Poetry and black
fmt:
    poetry run black .
    ruff

# Clean up generated files
clean:
    rm -rf **/__pycache__
    rm -rf **/.cache
    rm -rf **/.pytest_cache
    rm -rf **/.mypy_cache
    rm -rf **/build
    rm -rf **/dist
    rm -rf **/*.egg-info
    rm -rf **/htmlcov
    rm -rf **/.tox/
    rm -rf **/docs/_build

# Run the development environment (install, run, and watch for changes)
dev:
    just install
    just run


# # Create new Git tag
# git-tag: 
# # git tag -a "v{{version()}}" -m ""
# # git push origin "v{{version()}}"

# Bump major version
bump-major:
    poetry version major

# Bump minor version
bump-minor:
    poetry version minor

# Bump patch version
bump-patch:
    poetry version patch

