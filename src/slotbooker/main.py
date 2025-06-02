import os
import logging
import yaml
from .slotbooker import Booker
from retrying import retry

# Define file paths for configuration and classes
classes_path = os.path.join(os.path.dirname(__file__), "data/classes.yaml")
classes = yaml.safe_load(open(classes_path))


@retry(stop_max_attempt_number=3)
def production():
    """Slotbooker Main Function."""

    # Retrieve environment variables
    user = os.environ.get("OCTIV_USERNAME")
    password = os.environ.get("OCTIV_PASSWORD")

    # Initialize the Booker instance
    booker = Booker(
        base_url="https://app.octivfitness.com/login",
    )

    # Login and book the class
    booker.login(username=user, password=password)

    booker.switch_day()
    booker.book_class(
        class_dict=classes.get("class_dict"),
        enter_class=True,
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
    logging.info(
        "Slotbooker completed successfully."
    )  # TODO: correct logging output if fails


def development(ci_run=False):
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
    else:
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


def main():
    if os.environ.get("IS_TEST"):
        development(ci_run=True)
    else:
        production()


if __name__ == "__main__":
    main()
