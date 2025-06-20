import logging
from collections import defaultdict
from datetime import datetime

# from selenium.common.exceptions import NoSuchElementException
from .utils.alerts import AlertErrorHandler
from .utils.logging import CustomLogger, LogHandler
from .notifications.mailing import MailHandler  # Assuming MailHandler is in this module
from .utils.selenium_manager import SeleniumManager
from .utils.helpers import get_day
from slotbooker.utils.xpaths import XPath
import os
from enum import Enum, auto

# Set up custom logger
logging.setLoggerClass(CustomLogger)
logger = logging.getLogger(__name__)


class BookingState(Enum):
    SUCCESS = auto()
    FAIL = auto()
    NEUTRAL = auto()


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
        self.day = None
        self.booking_class_slot = None
        self.booking_time_slot = None
        self.booking_successful = BookingState.FAIL
        self.booking_information = {"bookings": []}

    def __continue_booking(self) -> bool:
        """Continues the booking process."""
        return True

    def __stop_booking(self) -> bool:
        """Stops the booking process."""
        logging.info("! Stopping booking process")
        return False

    def close_driver(self) -> None:
        self.selenium_manager.driver_is_initialialized()
        self.selenium_manager.close_driver()
        logging.info("WebDriver closed")

    def login(self, username: str, password: str) -> bool:
        self.selenium_manager.driver_is_initialialized()

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
        except ValueError as e:
            logging.warning("! ValueError during login entry")
            logging.error(e, exc_info=True)
            exit(1)
        except Exception as e:
            logging.error(f"! Unexpected Error during Login: {e}")
            exit(1)

        stop_booking = AlertErrorHandler.check_login_alert(
            selenium_manager=self.selenium_manager
        )

        if stop_booking:
            return self.__stop_booking()
        else:
            logging.success("Login successful")
            return self.__continue_booking()

    def switch_day(self) -> (str, str):
        self.selenium_manager.driver_is_initialialized()

        """Switch to the desired day for booking slots."""
        days_before_bookable = os.environ.get("DAYS_BEFORE_BOOKABLE", None)
        days_before_bookable = (
            int(days_before_bookable)
            if days_before_bookable and days_before_bookable.strip()
            else 0
        )

        if days_before_bookable is None:
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
            self.__stop_booking()
            raise e

        self.booking_information.update(
            {"current_date": f"{self.day}, {future_date.strftime('%d/%m/%Y')}"}
        )
        return self.day, future_date.strftime("%d/%m/%Y")

    def book_class(
        self, class_dict: dict, enter_class: bool = True
    ) -> (bool, str, str):
        """Book classes based on provided booking information."""

        self.selenium_manager.driver_is_initialialized()

        logging.info(f"{'Booking' if enter_class else 'Cancelling'} classes...")
        execution_booking_time = os.environ.get(
            "EXECUTION_BOOKING_TIME", "00:00:00.000000"
        )
        logging.info(
            f"Execution booking time set to {execution_booking_time} (HH:MM:SS.mmmmmm)"
        )

        self.class_dict = class_dict.get(self.day)

        # Load and transform the input class_dict into a list of unique class entries.
        class_entry_list = list({entry.get("class") for entry in self.class_dict})

        # Get all bounding boxes containing booking slots present in the current window.
        self.selenium_manager.wait_for_element(xpath=XPath.booking_section_head())
        all_slots_bounding_boxes = self.selenium_manager.find_elements(
            xpath=XPath.booking_section_head()
        )

        all_possible_booking_slots_dict = self._generate_bounding_box_class_dict(
            class_entry_list, all_slots_bounding_boxes, enter_class=enter_class
        )

        for entry in self.class_dict:
            if entry.get("class") == "None":
                logging.info("! No class set for this day.")
                self.booking_successful = BookingState.NEUTRAL
                return self.__stop_booking()

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
                self.booking_successful = BookingState.FAIL
                return self.__stop_booking()

            try:
                button_xpath = all_possible_booking_slots_dict[self.booking_class_slot][
                    self.booking_time_slot
                ]["xpath"]
                logging.info(
                    f"? Checking {self.booking_class_slot} at {self.booking_time_slot}..."
                )
            except KeyError:
                logging.info(
                    f"! No class of type {self.booking_class_slot} is present on {self.day} at {self.booking_time_slot}"
                )
                self.booking_successful = BookingState.FAIL
                return self.__stop_booking()

            if self._book_class_slot(
                button_xpath, prioritize_waiting_list, execution_booking_time
            ):
                self.booking_successful = BookingState.SUCCESS
                return self.__stop_booking()

        return self.__continue_booking()

    def _generate_bounding_box_class_dict(
        self,
        class_entry_list: list,
        all_slots_bounding_boxes: list,
        enter_class: bool = True,
    ) -> dict:
        """Get all possible booking slots for specified class entries and bounding boxes."""
        logging.info(f"? Possible classes: {class_entry_list}")

        all_possible_booking_slots_dict = defaultdict(dict)

        for slot_index, box in enumerate(all_slots_bounding_boxes, start=1):
            try:
                class_name = self.selenium_manager.get_element_text(
                    xpath=XPath.bounding_box_label(
                        slot_index=slot_index,
                        enter_class=enter_class,
                    )
                )
                if class_name in class_entry_list:
                    time_slot = self.selenium_manager.get_element_text(
                        xpath=XPath.bounding_box_time(
                            slot_index=slot_index,
                            enter_class=enter_class,
                        )
                    )
                    logging.info(f"- Time: {time_slot} - Class: {class_name}")

                    button_book = (
                        XPath.enter_slot(slot=slot_index)
                        if enter_class
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
        execution_booking_time: str = "00:00:00.000000",
    ) -> bool:
        """Book a specific class slot."""
        logging.info(f"> Booking {self.booking_class_slot} at {self.booking_time_slot}")

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
            return self.__stop_booking()
        else:
            logging.success("Class booked")
            return self.__continue_booking()

    def send_result(
        self,
        sender: str,
        password: str,
        receiver: str,
        format: str = "plain",
        attach_logfile: bool = False,
        send_mail: list[str] = None,
    ) -> None:
        """
        Configure and send booking result notification via email.

        Args:
            sender (str): Sender's email address.
            password (str): Sender's email password.
            receiver (str): Receiver's email address.
            format (str): Email format, "plain" or "html".
            attach_logfile (bool): Whether to attach a log file.
            send_mail (list): Which types of emails to send ("on_success", "on_failure", "on_neutral").
        """
        if send_mail is None:
            send_mail = ["on_success", "on_failure", "on_neutral"]

        self.mail_handler = MailHandler(
            email_sender=sender,
            email_password=password,
            email_receiver=receiver,
            format=format,
        )

        attachment_path = (
            self.loggingHandler.get_log_file_path() if attach_logfile else None
        )

        def handle_success():
            self.mail_handler.send_successful_booking_email(
                booking_information=self.booking_information,
                attachment_path=attachment_path,
            )
            logging.success(f"Booked successfully {self.booking_class_slot}")

        def handle_neutral():
            self.mail_handler.send_no_classes_email(
                booking_date=self.booking_information["current_date"],
                attachment_path=attachment_path,
            )

        def handle_failure():
            self.mail_handler.send_unsuccessful_booking_email(
                booking_information=self.booking_information,
                attachment_path=attachment_path,
            )

        handlers = [
            (
                self.booking_successful == BookingState.SUCCESS
                and "on_success" in send_mail,
                handle_success,
            ),
            (
                self.booking_successful == BookingState.NEUTRAL
                and "on_neutral" in send_mail,
                handle_neutral,
            ),
            (
                self.booking_successful == BookingState.FAIL
                and "on_failure" in send_mail,
                handle_failure,
            ),
        ]

        self.close_driver()
        # Dispatch table with conditions in priority order
        for condition, handler in handlers:
            if condition:
                handler()
                break
