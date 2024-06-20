# Aliases
alias docker := docker-full
alias gpa := git-push-all

# Show the help
# omitted _default command is triggered when running "just"
_default:
    @just --list --unsorted

# Install project dependencies and pre-commit hooks
install:
    brew install poetry
    pre-commit install
    poetry install

# Run pre-commit hooks
pre-commit:
    pre-commit run --all-files

# Run the slotBooker application
run:
    poetry run slotBooker

# Run the slotBookerDev application
run-dev:
    poetry run slotBookerDev

# Build Docker image
docker-build:
    poetry_version=$(poetry version | awk '{print $2}')
    docker build -t slotbookertest:${poetry_version} -f poetry.Dockerfile .

# Run Docker container
docker-run:
    poetry_version=$(poetry version | awk '{print $2}')
    docker run -it --env-file .env \
    --volume $(pwd)/octiv-booker/src/slotbooker/data/:/app/slotbooker/data/ \
    slotbookertest:${poetry_version}

# Build and run Docker container
docker-full:
    just docker-build
    just docker-run

# Install project dependencies using Poetry and virtual environment
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
    poetry run ruff

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
    rm -rf .venv

# Create new Git tag
git-tag: 
    #!/usr/bin/env bash
    poetry_version=$(poetry version | awk '{print $2}')
    git tag -a "v${poetry_version}" -m ""
    git push origin "v${poetry_version}"

# Add, commit, tag, and push changes to Git
git-push-all message:
    #!/usr/bin/env bash
    git add .
    git commit -m "{{message}}"
    poetry_version=$(poetry version | awk '{print $2}')
    git tag -a "v${poetry_version}" -m ""
    git push origin "v${poetry_version}"

# Bump major version
bump-major:
    poetry version major

# Bump minor version
bump-minor:
    poetry version minor

# Bump patch version
bump-patch:
    poetry version patch
