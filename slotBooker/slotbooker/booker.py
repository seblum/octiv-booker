import datetime
import os
import sys

import yaml

from .driver import close_driver, get_driver
from .helper_functions import start_logging, stop_logging
from .ui_interaction import Booker

# Load config yaml
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))


def main():
    """Main of Slotbooker. Gets driver, logs into website, selects
    the day wanted, and books slot. Closes driver afterwards
    """
    # start writing output to logfile
    # file, orig_stdout = start_logging()

    # get env variables
    USER = os.environ.get("OCTIV_USERNAME")
    PASSWORD = os.environ.get("OCTIV_PASSWORD")

    # check whether env variables are set or None
    if USER is None or PASSWORD is None:
        print("USERNAME and PASSWORD not set")
        print("Please run 'source set-credentials.sh' if running local")
    else:
        print("USERNAME and PASSWORD prevalent")
        print(f"USER: {USER}")

        driver = get_driver(chromedriver=config.get("chromedriver"))

        booker = Booker(
            driver=driver,
            days_before_bookable=config.get("days_before_bookable"),
            base_url=config.get("base_url"),
        )

        booker.login(username=USER, password=PASSWORD)
        booker.switch_day()
        booker.book_class(
            class_list=config.get("class_list"), booking_action=config.get("book_class")
        )

        # close_driver(driver)

    # stop_logging(file, orig_stdout)


if __name__ == "__main__":
    main()
