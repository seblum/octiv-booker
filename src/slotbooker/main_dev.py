import os
import logging
import yaml

from .booking_handler import Booker
# from .utils.mail_handler import MailHandler

# Load config yaml
config_path = os.path.join(os.path.dirname(__file__), "utils/config.yaml")
config = yaml.safe_load(open(config_path))

classes_path = os.path.join(os.path.dirname(__file__), "data/classes.yaml")
classes = yaml.safe_load(open(classes_path))


def main(retry: int = 2):
    # get env variables
    user = os.environ.get("OCTIV_USERNAME")
    password = os.environ.get("OCTIV_PASSWORD")
    days_before_bookable = int(os.environ.get("DAYS_BEFORE_BOOKABLE", 0))
    execution_booking_time = os.environ.get("EXECUTION_BOOKING_TIME")

    # check whether env variables are set or None
    logging.info(f"Log in as: {user}")

    for attempt in range(1, retry + 1):
        booker = Booker(
            chromedriver=config.get("chromedriver"),
            days_before_bookable=days_before_bookable,
            base_url=config.get("base_url"),
            execution_booking_time=execution_booking_time,
            env="dev",
        )

        booker.login(username=user, password=password)
        booker.switch_day()

        success, _, _ = booker.book_class(
            class_dict=classes.get("class_dict"),
            booking_action=classes.get("book_class"),
        )

        # Configure mailing settings && send mail
        booker.send_result(
            sender=os.getenv("EMAIL_SENDER"),
            password=os.getenv("EMAIL_PASSWORD"),
            receiver=os.getenv("EMAIL_RECEIVER"),
            format="html",
            attachment_path=None,
        )

        booker.close()
        logging.success(f"Attempt {attempt}: OctivBooker succeeded")


if __name__ == "__main__":
    main()
