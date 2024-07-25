import logging
from collections import defaultdict
from datetime import datetime

# from selenium.common.exceptions import NoSuchElementException
import time
from .alert_error_handler import AlertErrorHandler
from .helper_functions import XPathHelper, BookingHelper
from .utils.log_handler import CustomLogger, LogHandler
from .utils.mail_handler import MailHandler  # Assuming MailHandler is in this module
from .utils.selenium_manager import SeleniumManager

# Set up custom logger
logging.setLoggerClass(CustomLogger)
logger = logging.getLogger(__name__)


class Booker:
    """
    A class representing a booking agent for Octiv.

    Attributes:
        driver (object): The Selenium WebDriver instance.
        base_url (str): The base URL of the booking website.
        days_before_bookable (int): Number of days before a class becomes bookable.
        execution_booking_time (str): Time the booking is executed.
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
        chromedriver: str,
        base_url: str,
        days_before_bookable: int,
        execution_booking_time: str,
        env: str = "prd",
    ):
        self.selenium_manager = SeleniumManager(chromedriver, env)
        self.base_url = base_url
        self.days_before_bookable = days_before_bookable
        self.execution_booking_time = execution_booking_time
        self.xpath_helper = XPathHelper()
        self.booking_helper = BookingHelper()
        self.warning_prompt_helper = AlertErrorHandler(
            driver=self.selenium_manager.get_driver(),
            selenium_manager=self.selenium_manager,
        )
        self.log_handler = LogHandler(log_level=logging.INFO)
        self.mail_handler = None
        self.class_dict = None
        self.booking_action = None
        self.day = None
        self.booking_class_slot = None
        self.booking_time_slot = None
        self.booking_successful = False
        self.booking_information = {"bookings": []}

    def login(self, username: str, password: str) -> bool:
        """Login to the booking website using the provided credentials."""
        try:
            logging.info(f"Log in as: {username}")

            self.selenium_manager.get_page(base_url=self.base_url)

            self.selenium_manager.input_text(
                self.xpath_helper.get_xpath_login_username_head() + "/div[1]/input",
                username,
            )
            self.selenium_manager.click_button(
                self.xpath_helper.get_xpath_login_username_head() + "/button"
            )
            logging.info("Username submitted successfully")

            self.selenium_manager.input_text(
                self.xpath_helper.get_xpath_login_password_head() + "/div[2]/input",
                password,
            )
            self.selenium_manager.click_button(
                self.xpath_helper.get_xpath_login_password_head()
                + "/div[3]/div/div/div[1]/div/i"
            )
            self.selenium_manager.click_button(
                self.xpath_helper.get_xpath_login_password_head() + "/button"
            )
        except Exception as e:
            logging.error(f"! Error during login attempt: {e}")

        try:
            alert_text = self._check_login_alert()
            if alert_text and any(
                keyword.lower() in alert_text.lower()
                for keyword in ["credentials", "Fehler"]
            ):
                logging.error(f"Incorrect credentials: {alert_text}")
                return self.booking_helper.stop_booking_process()
        except Exception:
            pass

        logging.success("Login successful")
        return not self.booking_helper.stop_booking_process()

    def switch_day(self) -> (str, str):
        """Switch to the desired day for booking slots."""
        future_date, diff_week = self.booking_helper.get_day(self.days_before_bookable)
        self.day = future_date.strftime("%A")

        try:
            for _ in range(diff_week):
                self.selenium_manager.click_button(
                    self.xpath_helper.get_xpath_booking_head() + "[3]/div[9]/div/div/i"
                )
                logging.info("Switched to following week")

            day_button = self.booking_helper.get_day_button(self.day, self.xpath_helper)
            self.selenium_manager.click_button(day_button)
            logging.info(f"Booking on {self.day}, {future_date}")
        except Exception as e:
            logging.error(f"! Error during day switch: {e}")

        self.booking_information.update(
            {"current_date": f"{self.day}, {future_date.strftime('%d/%m/%Y')}"}
        )
        return self.day, future_date.strftime("%d/%m/%Y")

    def book_class(
        self, class_dict: dict, booking_action: bool = True
    ) -> (bool, str, str):
        """Book classes based on provided booking information."""
        self.booking_action = booking_action
        self.class_dict = class_dict.get(self.day)
        class_entry_list = self._load_and_transform_input_class_dict()

        all_slots_bounding_boxes = self._get_all_bounding_boxes_in_window()
        all_possible_booking_slots_dict = self._get_all_bounding_boxes_by_class_name(
            class_entry_list, all_slots_bounding_boxes
        )

        for entry in self.class_dict:
            if entry.get("class") == "None":
                logging.info("! No class set for this day.")
                return (
                    self.booking_successful,
                    self.booking_class_slot,
                    self.booking_time_slot,
                )
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
                return (
                    self.booking_successful,
                    self.booking_class_slot,
                    self.booking_time_slot,
                )
            button_xpath = self._get_button_xpath(all_possible_booking_slots_dict)
            if not button_xpath:
                logging.info(
                    f"! No class {self.booking_class_slot} found for this day."
                )
                return (
                    self.booking_successful,
                    self.booking_class_slot,
                    self.booking_time_slot,
                )

            if self._book_class_slot(button_xpath, prioritize_waiting_list):
                return (
                    self.booking_successful,
                    self.booking_class_slot,
                    self.booking_time_slot,
                )

        return self.booking_successful, self.booking_class_slot, self.booking_time_slot

    def _load_and_transform_input_class_dict(self) -> list:
        """Load and transform the input class_dict into a list of unique class entries."""
        return list({entry.get("class") for entry in self.class_dict})

    def _get_all_bounding_boxes_in_window(self) -> list:
        """Get all bounding boxes containing booking slots present in the current window."""
        self.selenium_manager.wait_for_element(
            xpath=self.xpath_helper.get_xpath_booking_head()
        )
        return self.selenium_manager.find_elements(
            xpath=self.xpath_helper.get_xpath_booking_head()
        )

    def _get_all_bounding_boxes_by_class_name(
        self, class_entry_list: list, all_slots_bounding_boxes: list
    ) -> dict:
        """Get all possible booking slots for specified class entries and bounding boxes."""
        logging.info(f"? Possible classes: {class_entry_list}")

        bounding_box_number_by_action = 1 if self.booking_action else 2
        all_possible_booking_slots_dict = defaultdict(list)

        for slot_index, box in enumerate(all_slots_bounding_boxes, start=1):
            xpath_test = f"{self.xpath_helper.get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
            try:
                textfield = self.selenium_manager.get_element_text(xpath=xpath_test)
                if textfield in class_entry_list:
                    time_slot = self.selenium_manager.get_element_text(
                        xpath=f"{self.xpath_helper.get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                    )
                    logging.info(f"- Time: {time_slot} - Class: {textfield}")

                    xpath_button_book = self.xpath_helper.get_xpath_booking_slot(
                        slot=slot_index, book_action=self.booking_action
                    )
                    all_possible_booking_slots_dict[textfield].append(
                        {
                            time_slot: {
                                "xpath": xpath_button_book,
                            }
                        }
                    )
            except Exception:
                continue

        return all_possible_booking_slots_dict

    def _get_button_xpath(self, all_possible_booking_slots_dict: dict) -> str:
        """Get the XPath of the button for booking a class slot."""
        try:
            all_possible_booking_slots_dict_flatten = {
                k: v
                for d in all_possible_booking_slots_dict.get(
                    self.booking_class_slot, []
                )
                for k, v in d.items()
            }

            button_xpath = all_possible_booking_slots_dict_flatten.get(
                self.booking_time_slot, {}
            ).get("xpath")
            logging.info(
                f"? Checking {self.booking_class_slot} at {self.booking_time_slot}..."
            )
            return button_xpath
        except (AttributeError, TypeError):
            logging.info(
                f"! No class of type {self.booking_class_slot} is present on {self.day} at {self.booking_time_slot}"
            )
            return None

    def _book_class_slot(
        self,
        button_xpath: str,
        prioritize_waiting_list: bool,
    ) -> bool:
        """Book a specific class slot."""
        logging.info(f"> Booking {self.booking_class_slot} at {self.booking_time_slot}")

        self._click_book_button(button_xpath)

        alert_obj = self.warning_prompt_helper.alert_is_present()
        if alert_obj:
            evaluate_result = self.warning_prompt_helper.evaluate_alert(
                alert_obj, prioritize_waiting_list
            )
            if evaluate_result is False:
                pass

            return evaluate_result

        error_text = self.warning_prompt_helper.error_is_present()
        if error_text:
            # TODO: Remove sleep
            time.sleep(3)
            return self.warning_prompt_helper.evaluate_error(error_text)

        logging.success("Class booked")
        self.booking_successful = True
        return self.booking_helper.stop_booking_process()

    def _click_book_button(self, xpath_button_book: str) -> None:
        """Click the book button using JavaScript execution."""
        element = self.selenium_manager.find_element(xpath=xpath_button_book)
        while True:
            current_time = datetime.now().time().strftime("%H:%M:%S.%f")
            if current_time >= self.execution_booking_time:
                start_time = datetime.now()
                logging.info(f"Start execution at {current_time}")
                self.selenium_manager.execute_script(
                    script="arguments[0].click();", element=element
                )
                end_time = datetime.now()
                logging.info(f"Executed at {end_time.time()}")
                logging.info(f"Took {(end_time - start_time).total_seconds()}s")
                break

    def _check_login_alert(self) -> str:
        """Check for alert messages after login."""
        # try:
        alert_div = self.selenium_manager.wait_for_element(
            xpath=self.xpath_helper.get_xpath_login_error_window(), timeout=10
        )
        return alert_div.text
        # except NoSuchElementException:
        #     return ""

    def close(self):
        """Closes the WebDriver."""
        self.selenium_manager.close_driver()

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
            attachment_path = self.log_handler.get_log_file_path()

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
