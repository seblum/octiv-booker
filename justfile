# Show the help
# ommited _default command is triggered when running "just"
_default:
    @just --list --unsorted

# # Show the current environment
# show: ##
#     @echo "Current environment:"
#     @poetry env info



# # Create a virtual environment
# venv:
#     export POETRY_VIRTUALENVS_IN_PROJECT=true && \

# Run pre-commit hooks
pre-commit:
    pre-commit run --all-files

run:
    poetry run slotBooker

run-dev:
    poetry run slotBookerDev

# Install project dependencies using Poetry
install-venv:
    python3 -m venv .venv
    source .venv/bin/activate
    pre-commit install
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
@clean:
    echo "🧹 Cleaning repository 🧹"
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".cache" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".mypy_cache" -exec rm -rf {} +
    find . -type d -name "build" -exec rm -rf {} +
    find . -type d -name "dist" -exec rm -rf {} +
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name "htmlcov" -exec rm -rf {} +
    find . -type d -name ".tox" -exec rm -rf {} +
    find . -type d -name "_build" -path "*/docs/_build" -exec rm -rf {} +

# Remove the installed virtual environment
clean-venv: 
    rm -r .venv



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

