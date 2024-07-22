import os
import logging
import yaml

from .booking_handler import Booker
# from .utils.mail_handler import MailHandler
from .utils.log_handler import LogHandler

# Load config yaml
config_path = os.path.join(os.path.dirname(__file__), "utils/config.yaml")
config = yaml.safe_load(open(config_path))

classes_path = os.path.join(os.path.dirname(__file__), "data/classes.yaml")
classes = yaml.safe_load(open(classes_path))


def main(retry: int = 3):
    log_hander = LogHandler(log_level=logging.INFO)

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
            env="dev"
            )

        # Configure mailing settings
        booker.set_mailing(
            sender = os.getenv("EMAIL_SENDER"),
            password = os.getenv("EMAIL_PASSWORD"),
            receiver = os.getenv("EMAIL_RECEIVER"),
            format="html"
            )

        booker.login(username=user, password=password)
        booking_day, booking_date = booker.switch_day()
        booking_date = f"{booking_day}, {booking_date}"

        booked_successful, class_slot, time_slot = booker.book_class(
            class_dict=classes.get("class_dict"),
            booking_action=classes.get("book_class"),
        )
        logging.success(f"Attempt {class_slot}: OctivBooker succeeded")

        booker.close()
        logging.success(f"Attempt {attempt}: OctivBooker succeeded")
        # response = "SUCCESS"

        # html_file = log_hander.convert_logs_to_html()

        # MailHandler(format="html").send_logs_to_mail(
        #     filename=html_file, response=response
        # )

        # if booked_successful:
        #     mail_handler.send_successful_booking_email(
        #         booking_date=booking_date,
        #         booking_time=time_slot,
        #         booking_name=class_slot,
        #         attachment_path=log_hander.get_log_file_path(),
        #     )
        # elif not booked_successful and class_slot is None and time_slot is None:
        #     mail_handler.send_no_classes_email(
        #         booking_date=booking_date,
        #         attachment_path=log_hander.get_log_file_path(),
        #     )
        # else:
        #     mail_handler.send_unsuccessful_booking_email(
        #         booking_date=booking_date,
        #         booking_time=time_slot,
        #         booking_name=class_slot,
        #         attachment_path=log_hander.get_log_file_path(),
        #     )


if __name__ == "__main__":
    main()
