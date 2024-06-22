# Octiv SlotBooker

![Octiv Overview](https://github.com/seblum/octiv_booker/blob/d434b11827b830aa7dd0e0614558034dbaabe66f/octiv_overview.png)

Octiv Slotbooker is a tool used to book slots/classes for the fitness app Octiv. It was developed to automate the weekly booking of classes, utilizing Selenium for its functionality.

## Structure

The repository includes the app itself written in Python and a Dockerfile under `slotBooker`. The directory structure is as follows:

```
OCTIV_BOOKER
│   README.md
│   justfile
│   poetry.Dockerfile
│   .pre-commit-config.yaml
│   LICENSE
│   pyproject.toml
│
└───.github/workflows
│
└───src
│   │   tests
│   │   ...
│   │
│   └───slotbooker
│       │   booker.py
│       │   ui_interaction.py
│       │   ...
│       │   
│       └───utils
│       │   │   driver.py
│       │   │   gmail.py
│       │   │   logging.py
│       │   │   ...
│       │   
│       └───data
│           │   classes.yaml

```

## Prerequisites

To run the app locally, you need to have the following installed and properly configured:

- Docker
- Chromedriver for Selenium (if running without Docker)

## Usage

### Local Development

Poetry is used for dependency management and running the application. For local development, ensure that the required environment variables are set. You can create a `.env` file in the root directory with the following content:

```bash
# .env
OCTIV_PASSWORD=password
EMAIL_SENDER=email@email.com
EMAIL_PASSWORD=password_2
EMAIL_RECEIVER=email@email.com
DAYS_BEFORE_BOOKABLE=1
EXECUTION_BOOKING_TIME=HH:MM:SS.XX
```

### Using the Justfile

To facilitate development, a `justfile` is provided. Here are some key commands:

```sh
# Run the application:**
just run

# Run the development version of the application:**
just run-dev

# Build the Docker image:**
just docker-build

# Run the Docker container:**
just docker-run

# Full Docker workflow (build and run):**
just docker-full
```

By using the provided `justfile` and the instructions above, you can easily set up and manage your development environment for Octiv SlotBooker.