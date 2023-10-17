from datetime import datetime
import os
import logging
import yaml
from selenium.common.exceptions import SessionNotCreatedException, NoSuchDriverException

from .driver import close_driver, get_driver
from .logging import setup_log_dir, start_logging, stop_logging
from .ui_interaction import Booker
from .gmail import send_logs_to_mail

# Load config yaml
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))


def main(retry: int = 3):
    """Slotbooker Main Function.

    This function represents the main flow of the Slotbooker application. It performs the following steps:
    - Starts writing output to a logfile using 'start_logging' function.
    - Retrieves environment variables 'OCTIV_USERNAME' and 'OCTIV_PASSWORD'.
    - If the required environment variables are not set, it informs the user to set them.
    - If the environment variables are set, it initializes a web driver and logs into the website.
    - Switches to the desired day and books a slot according to the configuration.
    - Closes the web driver after completing the booking process.
    - Stops logging and restores the original stdout using 'stop_logging' function.
    - Sends the log file to an email address using 'send_logs_to_mail' function.

    Returns:
        None: This function does not return anything.

    Example:
        Run this function to perform the slot booking process with the configured options:

        >>> main()
    """

    # start writing output to logfile
    # file, orig_stdout, dir_log_file = start_logging()

    dir_log_file = setup_log_dir()
    logging.basicConfig(
        filename=dir_log_file,
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s %(message)s",
        level=logging.INFO,
    )

    # get env variables
    USER = os.environ.get("OCTIV_USERNAME")
    PASSWORD = os.environ.get("OCTIV_PASSWORD")
    days_before_bookable_env = os.environ.get("DAYS_BEFORE_BOOKABLE")
    DAYS_BEFORE_BOOKABLE = int(days_before_bookable_env)
    
    # check whether env variables are set or None
    if USER is None or PASSWORD is None:
        logging.info("USERNAME and PASSWORD not set")
        logging.info("Please run 'source set-credentials.sh' if running local")
    else:
        logging.info("USERNAME and PASSWORD prevalent")
        logging.info(f"USER: {USER}")

        count = 0
        while count < retry:
            try:
                driver = get_driver(chromedriver=config.get("chromedriver"))

                booker = Booker(
                    driver=driver,
                    days_before_bookable=DAYS_BEFORE_BOOKABLE,
                    base_url=config.get("base_url"),
                )

                booker.login(username=USER, password=PASSWORD)
                booker.switch_day()
                booker.book_class(
                    class_dict=config.get("class_dict"),
                    booking_action=config.get("book_class"),
                )

                close_driver(driver)
                logging.info(f"OctivBooker succeeded | try: {count+1}")
                count = 3
            except SessionNotCreatedException:
                logging.info(f"OctivBooker failed | TRY: {count+1}")
                logging.info(f"! SessionNotCreatedException")
                count += 1
                continue
            except NoSuchDriverException:
                logging.info(f"OctivBooker failed | TRY: {count+1}")
                logging.info(f"! NoSuchDriverException")
                count += 1
                continue
            except:
                logging.info(f"OctivBooker failed | TRY: {count+1}")
                count += 1
                continue

        # stop_logging(file, orig_stdout)
        send_logs_to_mail(dir_log_file)


if __name__ == "__main__":
    main()
