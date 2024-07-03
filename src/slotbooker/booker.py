import os
import logging
import yaml
from selenium.common.exceptions import SessionNotCreatedException, NoSuchDriverException

from .utils.driver import close_driver, get_driver
from .utils.logging import LogHandler
from .ui_interaction import Booker
from .utils.settings import set_credentials

# Load configuration files
config_path = os.path.join(os.path.dirname(__file__), "utils/config.yaml")
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

classes_path = os.path.join(os.path.dirname(__file__), "data/classes.yaml")
with open(classes_path, "r") as file:
    classes = yaml.safe_load(file)


def main(retry: int = 3):
    """Slotbooker Main Function.

    This function represents the main flow of the Slotbooker application. It performs the following steps:
    - Starts writing output to a logfile using 'setup_log_dir'.
    - Retrieves environment variables 'OCTIV_USERNAME' and 'OCTIV_PASSWORD'.
    - If the required environment variables are not set, it informs the user to set them.
    - If the environment variables are set, it initializes a web driver and logs into the website.
    - Switches to the desired day and books a slot according to the configuration.
    - Closes the web driver after completing the booking process.
    - Sends the log file to an email address using 'send_logs_to_mail'.

    Returns:
        None: This function does not return anything.

    Example:
        Run this function to perform the slot booking process with the configured options:

        >>> main()
    """
    # start writing output to logfile
    # file, orig_stdout, dir_log_file = start_logging()

    log_hander = LogHandler()
    driver = get_driver(chromedriver=config.get("chromedriver"))

    if os.environ.get("IS_TEST"):
        logging.info("! Test env")
        print("! Test env")

        booker = Booker(
            driver=driver,
            days_before_bookable=0,
            base_url=config.get("base_url"),
            execution_booking_time="00:00:00.00",
        )
        user = os.environ.get("OCTIV_USERNAME")
        password = "if-this-would-be-the-password"

        login_failed = booker.login(username=user, password=password)
        if login_failed:
            logging.info("! Login failed as expected")
            print("TEST OK")
        exit()

    # dir_log_file = log_hander.setup_log_dir()
    # logging.basicConfig(
    #     filename=dir_log_file,
    #     filemode="w",
    #     encoding="utf-8",
    #     format="%(asctime)s %(message)s",
    #     level=logging.INFO,
    # )

    # Retrieve environment variables
    user = os.environ.get("OCTIV_USERNAME")
    password = os.environ.get("OCTIV_PASSWORD")
    days_before_bookable = int(os.environ.get("DAYS_BEFORE_BOOKABLE", 0))
    execution_booking_time = os.environ.get("EXECUTION_BOOKING_TIME")

    # Ensure credentials are set
    if not user or not password:
        logging.info("USERNAME and PASSWORD not set")
        set_credentials()
    else:
        logging.info(f"USER: {user}")

        for attempt in range(retry):
            try:
                booker = Booker(
                    driver=driver,
                    days_before_bookable=days_before_bookable,
                    base_url=config.get("base_url"),
                    execution_booking_time=execution_booking_time,
                )

                booker.login(username=user, password=password)
                booker.switch_day()
                booker.book_class(
                    class_dict=classes.get("class_dict"),
                    booking_action=classes.get("book_class"),
                )

                close_driver(driver)
                logging.info(f"| [{attempt + 1}] OctivBooker succeeded")
                response = "SUCCESS"
                break
            except (SessionNotCreatedException, NoSuchDriverException) as e:
                logging.info(f"| [{attempt + 1}] OctivBooker failed")
                logging.error(e, exc_info=True)
                response = "FAILED"
                continue
            except Exception as e:
                logging.info(f"| [{attempt + 1}] OctivBooker failed")
                logging.error(e, exc_info=True)
                response = "FAILED"
                continue

        html_file = log_hander.convert_logs_to_html()
        # stop_logging(file, orig_stdout)
        # log_hander.send_logs_to_mail(dir_log_file,response)
        log_hander.send_logs_to_mail(html_file, response, format="html")


if __name__ == "__main__":
    main()
