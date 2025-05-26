import logging
from collections import defaultdict
from datetime import datetime

# from selenium.common.exceptions import NoSuchElementException
from .utils.alerts import AlertErrorHandler
from .utils.logging import CustomLogger, LogHandler
from .notifications.mailing import MailHandler  # Assuming MailHandler is in this module
from .utils.selenium_manager import SeleniumManager
from .utils.helpers import stop_booking_process, get_day
from slotbooker.utils.xpaths import XPath
import os

# Set up custom logger
logging.setLoggerClass(CustomLogger)
logger = logging.getLogger(__name__)


class Booker:
    """
    A class representing a booking agent for Octiv.

    Attributes:
        driver (object): The Selenium WebDriver instance.
        base_url (str): The base URL of the booking website.
        class_dict (dict): Dictionary containing class booking information for a specific day.
        booking_action (bool): Indicates whether to perform booking actions (True) or not (False).
        day (str): The selected day for booking.

    Methods:
        login(username: str, password: str) -> None:
            Log in to the booking website using provided credentials.
        switch_day() -> str:
            Switch to the desired day for booking slots.
        book_class(class_dict: dict, booking_action: bool = True) -> None:
            Book classes based on provided booking information.
        close() -> None:
            Close the WebDriver.
    """

    def __init__(
        self,
        base_url: str,
        chromedriver: str = None,  # defaults to None, will use the default chromedriver path: "/usr/local/bin/chromedriver"
        env: str = "prd",
    ):
        self.base_url = base_url
        self.selenium_manager = SeleniumManager(chromedriver, env)

        self.loggingHandler = LogHandler(log_level=logging.INFO)
        self.mail_handler = None
        self.class_dict = None
        self.booking_action = None
        self.day = None
        self.booking_class_slot = None
        self.booking_time_slot = None
        self.booking_successful = False
        self.booking_information = {"bookings": []}

    def __return_bookings(self) -> (str, str, str):
        """Return the booking information."""
        return (
            self.booking_successful,
            self.booking_class_slot,
            self.booking_time_slot,
        )

    def login(self, username: str, password: str) -> bool:
        """Login to the booking website using the provided credentials."""
        try:
            logging.info(f"Log in as: {username}")

            self.selenium_manager.get_page(base_url=self.base_url)

            self.selenium_manager.input_text(
                XPath.login_username_input(),
                username,
            )
            self.selenium_manager.click_button(XPath.login_username_button())
            logging.info("Username submitted successfully")

            self.selenium_manager.input_text(
                XPath.login_password_input(),
                password,
            )
            self.selenium_manager.click_button(XPath.login_password_check())
            self.selenium_manager.click_button(XPath.login_password_button())
        except Exception as e:
            logging.error(f"! Error during username entry: {e}")

        stop_booking = AlertErrorHandler.check_login_alert(
            selenium_manager=self.selenium_manager
        )

        if stop_booking:
            return stop_booking_process()
        else:
            logging.success("Login successful")
            return not stop_booking_process

    def switch_day(self, days_before_bookable: str = None) -> (str, str):
        """Switch to the desired day for booking slots."""
        if days_before_bookable is None:
            days_before_bookable = int(os.environ.get("DAYS_BEFORE_BOOKABLE", 0))
            logging.info(
                f"Switching to day {days_before_bookable} days before bookable date"
            )

        future_date, diff_week = get_day(days_before_bookable)
        self.day = future_date.strftime("%A")

        try:
            for _ in range(diff_week):
                self.selenium_manager.click_button(XPath.switch_week_button())
                logging.info("Switched to following week")

            day_button = XPath.weekday_button(self.day)
            self.selenium_manager.click_button(day_button)
            logging.info(f"Booking on {self.day}, {future_date}")
        except Exception as e:
            logging.error(f"! Error during day switch: {e}")
            # TODO: make script fail if day switch fails

        self.booking_information.update(
            {"current_date": f"{self.day}, {future_date.strftime('%d/%m/%Y')}"}
        )
        return self.day, future_date.strftime("%d/%m/%Y")

    def book_class(
        self, class_dict: dict, booking_action: bool = True
    ) -> (bool, str, str):
        """Book classes based on provided booking information."""
        if booking_action:
            logging.info("Booking classes...")
        else:
            logging.info("Cancelling classes...")

        self.booking_action = booking_action
        self.class_dict = class_dict.get(self.day)

        # Load and transform the input class_dict into a list of unique class entries.
        class_entry_list = list({entry.get("class") for entry in self.class_dict})

        # Get all bounding boxes containing booking slots present in the current window.
        self.selenium_manager.wait_for_element(xpath=XPath.booking_section_head())
        all_slots_bounding_boxes = self.selenium_manager.find_elements(
            xpath=XPath.booking_section_head()
        )

        all_possible_booking_slots_dict = self._generate_bounding_box_class_dict(
            class_entry_list, all_slots_bounding_boxes
        )

        for entry in self.class_dict:
            if entry.get("class") == "None":
                logging.info("! No class set for this day.")
                return self.__return_bookings()

            self.booking_time_slot, self.booking_class_slot, prioritize_waiting_list = (
                entry.get("time"),
                entry.get("class"),
                entry.get("wl"),
            )
            self.booking_information["bookings"].append(
                {"time": entry.get("time"), "class": entry.get("class")}
            )

            if not all_possible_booking_slots_dict:
                logging.info("! No classes found overall for this day.")
                return self.__return_bookings()

            try:
                button_xpath = all_possible_booking_slots_dict[self.booking_class_slot][
                    self.booking_time_slot
                ]["xpath"]
                logging.info(
                    f"? Checking {self.booking_class_slot} at {self.booking_time_slot}..."
                )
            except KeyError:
                button_xpath = None
                logging.info(
                    f"! No class of type {self.booking_class_slot} is present on {self.day} at {self.booking_time_slot}"
                )

            if not button_xpath:
                logging.info(
                    f"! No class {self.booking_class_slot} found for this day."
                )
                return self.__return_bookings()

            if self._book_class_slot(button_xpath, prioritize_waiting_list):
                return self.__return_bookings()

        return self.booking_successful, self.booking_class_slot, self.booking_time_slot

    def _generate_bounding_box_class_dict(
        self, class_entry_list: list, all_slots_bounding_boxes: list
    ) -> dict:
        """Get all possible booking slots for specified class entries and bounding boxes."""
        logging.info(f"? Possible classes: {class_entry_list}")

        # book class = 1, cancel class = 2
        class_action = 1 if self.booking_action else 2
        all_possible_booking_slots_dict = defaultdict(dict)

        for slot_index, box in enumerate(all_slots_bounding_boxes, start=1):
            try:
                class_name = self.selenium_manager.get_element_text(
                    xpath=XPath.bounding_box_label(
                        slot_index=slot_index,
                        bounding_box_number=class_action,
                    )
                )
                if class_name in class_entry_list:
                    time_slot = self.selenium_manager.get_element_text(
                        xpath=XPath.bounding_box_time(
                            slot_index=slot_index,
                            bounding_box_number=class_action,
                        )
                    )
                    logging.info(f"- Time: {time_slot} - Class: {class_name}")

                    button_book = (
                        XPath.enter_slot(slot=slot_index)
                        if self.booking_action
                        else XPath.cancel_slot(slot=slot_index)
                    )

                    all_possible_booking_slots_dict[class_name][time_slot] = {
                        "xpath": button_book
                    }
            except Exception:
                continue

        return all_possible_booking_slots_dict

    def _book_class_slot(
        self,
        button_xpath: str,
        prioritize_waiting_list: bool,
    ) -> bool:
        """Book a specific class slot."""
        logging.info(f"> Booking {self.booking_class_slot} at {self.booking_time_slot}")

        execution_booking_time = os.environ.get(
            "EXECUTION_BOOKING_TIME", "00:00:00.000000"
        )
        logging.info(
            f"Execution booking time set to {execution_booking_time} (HH:MM:SS.mmmmmm)"
        )

        # self._click_book_button(button_xpath)
        element = self.selenium_manager.find_element(xpath=button_xpath)
        while True:
            current_time = datetime.now().time().strftime("%H:%M:%S.%f")

            if current_time >= execution_booking_time:
                start_time = datetime.now()
                logging.info(f"Start execution at {current_time}")
                self.selenium_manager.execute_script(
                    script="arguments[0].click();", element=element
                )
                end_time = datetime.now()
                logging.info(f"Executed at {end_time.time()}")
                logging.info(f"Took {(end_time - start_time).total_seconds()}s")
                break

        stop_booking = AlertErrorHandler.check_booking_alert(
            selenium_manager=self.selenium_manager, waiting_list=prioritize_waiting_list
        )

        if stop_booking:
            logging.error("Booking process stopped due to an error.")
            return stop_booking_process()
        else:
            logging.success("Class booked")
            self.booking_successful = True
            return stop_booking_process

    def send_result(
        self,
        sender: str,
        password: str,
        receiver: str,
        format: str = "plain",
        attach_logfile=False,
    ) -> None:
        """
        Configure email settings for sending notifications.

        Args:
            sender (str): The email address of the sender.
            password (str): The password of the sender's email account.
            receiver (str): The email address of the receiver.
            format (str): The format of the email body ("plain" or "html").
        """
        self.mail_handler = MailHandler(
            email_sender=sender,
            email_password=password,
            email_receiver=receiver,
            format=format,
        )

        attachment_path = None
        if attach_logfile:
            attachment_path = self.loggingHandler.get_log_file_path()

        if self.booking_successful:
            self.mail_handler.send_successful_booking_email(
                booking_information=self.booking_information,
                attachment_path=attachment_path,
            )
            logging.success(f"Booked successfully {self.booking_class_slot}")
        elif self.booking_successful is False and self.booking_class_slot is None:
            self.mail_handler.send_no_classes_email(
                booking_date=self.booking_information["current_date"],
                attachment_path=attachment_path,
            )
        else:
            self.mail_handler.send_unsuccessful_booking_email(
                booking_information=self.booking_information,
                attachment_path=attachment_path,
            )

    def close(self):
        """Closes the WebDriver."""
        self.selenium_manager.close_driver()
        logging.info("WebDriver closed")
