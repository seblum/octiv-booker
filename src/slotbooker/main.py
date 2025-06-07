import os
import logging
import yaml
from .slotbooker import Booker
from tenacity import retry, stop_after_attempt


# Define file paths for configuration and classes
parent_dir = os.path.dirname(os.path.dirname(__file__))
classes_path = os.path.join(parent_dir, "data/classes.yaml")
print(classes_path)
classes = yaml.safe_load(open(classes_path))


@retry(
    stop=stop_after_attempt(3),
    before=lambda retry_state: print(f"Attempt #{retry_state.attempt_number}"),
    reraise=False,  # Do not raise RetryError
)
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
    result = booker.book_class(
        class_dict=classes.get("class_dict"),
        enter_class=True,
    )
    if not result:
        raise ValueError(
            f"Booking failed for class: {classes.get('class_dict').get('name')}"
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
    # TODO: make mailhander static


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
            # booking_action=classes.get("book_class"),
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

        # booker.close()


def main():
    if os.environ.get("IS_TEST"):
        development(ci_run=True)
    else:
        production()


if __name__ == "__main__":
    main()
