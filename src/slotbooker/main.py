import os
import logging
import yaml
from .slotbooker import Booker


# Define file paths for configuration and classes
parent_dir = os.path.dirname(os.path.dirname(__file__))
classes_path = os.path.join(parent_dir, "data/classes.yaml")

classes = yaml.safe_load(open(classes_path))


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
        send_mail=["on_failure", "on_neutral"],  # Set to False for testing
    )


def development(ci_run=False):
    # get env variables
    user = os.environ.get("OCTIV_USERNAME")
    if ci_run:
        password = "if-this-would-be-the-password"
        env = "prd"
    else:
        password = os.environ.get("OCTIV_PASSWORD")
        env = "dev"

    booker = Booker(
        base_url="https://app.octivfitness.com/login",
        env=env,
    )

    login_successfull = booker.login(username=user, password=password)
    if not login_successfull:
        logging.info("TEST OK | Login failed as expected")
        print("TEST OK | Login failed as expected")
    else:
        booker.switch_day()

        booker.book_class(
            class_dict=classes.get("class_dict"),
        )

        # Configure mailing settings && send mail
        # booker.send_result(
        #     sender=os.getenv("EMAIL_SENDER"),
        #     password=os.getenv("EMAIL_PASSWORD"),
        #     receiver=os.getenv("EMAIL_RECEIVER"),
        #     format="html",
        #     attach_logfile=True,
        #     send_mail=["on_failure", "on_neutral"],  # Set to False for testing
        # )


def main():
    if os.environ.get("IS_TEST"):
        development(ci_run=True)
    else:
        production()


if __name__ == "__main__":
    main()
