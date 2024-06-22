import os
import logging
import yaml

from .utils.driver import close_driver, get_driver
from .ui_interaction import Booker

# from .utils.logging import start_logging, stop_logging
from .utils.settings import set_credentials

# Load config yaml
config_path = os.path.join(os.path.dirname(__file__), "utils/config.yaml")
config = yaml.safe_load(open(config_path))

classes_path = os.path.join(os.path.dirname(__file__), "data/classes.yaml")
classes = yaml.safe_load(open(classes_path))


def main(retry: int = 3):
    # start writing output to logfile
    #  file, orig_stdout, dir_log_file = start_logging()

    # dir_log_file = setup_log_dir()
    logging.basicConfig(
        # filename=dir_log_file,
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s %(message)s",
        level=logging.INFO,
    )

    # get env variables
    user = os.environ.get("OCTIV_USERNAME")
    password = os.environ.get("OCTIV_PASSWORD")
    days_before_bookable = int(os.environ.get("DAYS_BEFORE_BOOKABLE"))
    execution_booking_time = os.environ.get("EXECUTION_BOOKING_TIME")

    # check whether env variables are set or None
    if user is None or password is None:
        logging.info("USERNAME and PASSWORD not set")
        set_credentials()  # Call the function to set credentials if not already set
    else:
        logging.info(f"USER: {user}")

    count = 0
    while count < retry:
        driver = get_driver(chromedriver=config.get("chromedriver"), env="dev")

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
        logging.info(f"| [{count+1}] OctivBooker succeeded")
        count = 3

        # stop_logging(file, orig_stdout)
        # send_logs_to_mail(dir_log_file)


if __name__ == "__main__":
    main()
