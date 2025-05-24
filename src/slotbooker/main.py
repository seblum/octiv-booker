import os
import logging
import yaml
from selenium.common.exceptions import SessionNotCreatedException, NoSuchDriverException
from .booker import Booker

# Define file paths for configuration and classes
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "utils/config.yaml")
CLASSES_PATH = os.path.join(os.path.dirname(__file__), "data/classes.yaml")


# Load configuration files
def load_yaml(file_path):
    """Load YAML configuration from a file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


config = load_yaml(CONFIG_PATH)
classes = load_yaml(CLASSES_PATH)


def main(retry: int = 3):
    """Slotbooker Main Function."""

    # Check if testing environment is set
    if os.environ.get("IS_TEST"):
        logging.info("Testing Docker Container")
        booker = Booker(
            chromedriver=config.get("chromedriver"),
            days_before_bookable=0,
            base_url=config.get("base_url"),
            execution_booking_time="00:00:00.00",
        )
        user = os.environ.get("OCTIV_USERNAME")
        test_password = "if-this-would-be-the-password"

        login_failed = booker.login(username=user, password=test_password)
        if login_failed:
            logging.info("TEST OK | Login failed as expected")

        booker.close()
        exit()

    # Retrieve environment variables
    user = os.environ.get("OCTIV_USERNAME")
    password = os.environ.get("OCTIV_PASSWORD")
    days_before_bookable = int(os.environ.get("DAYS_BEFORE_BOOKABLE", 0))
    execution_booking_time = os.environ.get("EXECUTION_BOOKING_TIME")

    for attempt in range(1, retry + 1):
        try:
            # Initialize the Booker instance
            booker = Booker(
                chromedriver=config.get("chromedriver"),
                days_before_bookable=days_before_bookable,
                base_url=config.get("base_url"),
                execution_booking_time=execution_booking_time,
            )

            # Login and book the class
            if booker.login(username=user, password=password):
                raise ValueError("Login failed")

            booker.switch_day()
            booker.book_class(
                class_dict=classes.get("class_dict"),
                booking_action=classes.get("book_class"),
            )

            # Send results via email
            booker.send_result(
                sender=os.getenv("EMAIL_SENDER"),
                password=os.getenv("EMAIL_PASSWORD"),
                receiver=os.getenv("EMAIL_RECEIVER"),
                format="html",
                attach_logfile=True,
            )

            # Close the Booker instance
            booker.close()
            logging.info(f"Attempt {attempt}: OctivBooker succeeded")
            break

        except (SessionNotCreatedException, NoSuchDriverException) as e:
            logging.warning(
                f"Attempt {attempt}: OctivBooker failed due to driver issue"
            )
            logging.error(e, exc_info=True)
        except ValueError as e:
            logging.warning(f"Attempt {attempt}: OctivBooker failed due to login issue")
            logging.error(e, exc_info=True)
        except Exception as e:
            logging.warning(
                f"Attempt {attempt}: OctivBooker failed due to unexpected error"
            )
            logging.error(e, exc_info=True)


if __name__ == "__main__":
    main()
