import os
import yaml
from .slotbooker import Booker
import logging

classes_path = os.path.join(os.path.dirname(__file__), "data/classes.yaml")
classes = yaml.safe_load(open(classes_path))


def main_dev(ci_run=False):
    # get env variables
    user = os.environ.get("OCTIV_USERNAME")
    if ci_run:
        password = "if-this-would-be-the-password"
    else:
        password = os.environ.get("OCTIV_PASSWORD")

    booker = Booker(
        base_url="https://app.octivfitness.com/login",
        env="dev",
    )

    login_failed = booker.login(username=user, password=password)
    if login_failed:
        logging.info("TEST OK | Login failed as expected")
    booker.switch_day()

    success, _, _ = booker.book_class(
        class_dict=classes.get("class_dict"),
        # booking_action=classes.get("book_class"),
    )

    # Configure mailing settings && send mail
    # booker.send_result(
    #     sender=os.getenv("EMAIL_SENDER"),
    #     password=os.getenv("EMAIL_PASSWORD"),
    #     receiver=os.getenv("EMAIL_RECEIVER"),
    #     format="html",
    #     attach_logfile=True,
    # )

    # booker.close()


if __name__ == "__main__":
    main_dev()
