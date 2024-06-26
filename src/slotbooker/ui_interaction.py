import logging
from collections import defaultdict
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as exco
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from .alerts_and_errors import WarningPromptHelper

from .helper_functions import XPathHelper, BookingHelper


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
    """

    def __init__(
        self,
        driver: object,
        base_url: str,
        days_before_bookable: int,
        execution_booking_time: str,
    ):
        self.driver = driver
        self.base_url = base_url
        self.days_before_bookable = days_before_bookable
        self.execution_booking_time = execution_booking_time
        self.class_dict = None
        self.booking_action = None
        self.day = None
        self.xpath_helper = XPathHelper()
        self.booking_helper = BookingHelper()
        self.warning_prompt_helper = WarningPromptHelper(self.driver)

    def login(self, username: str, password: str) -> bool:
        """Login to the booking website using the provided credentials."""
        try:
            self.driver.get(self.base_url)

            self._input_text(
                self.xpath_helper.get_xpath_login_username_head() + "/div[1]/input",
                username,
            )
            self._click_button(
                self.xpath_helper.get_xpath_login_username_head() + "/button"
            )
            logging.info("| Username submitted successfully")

            self._input_text(
                self.xpath_helper.get_xpath_login_password_head() + "/div[2]/input",
                password,
            )
            self._click_button(
                self.xpath_helper.get_xpath_login_password_head()
                + "/div[3]/div/div/div[1]/div/i"
            )
            self._click_button(
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
                logging.info(f"! Incorrect credentials: {alert_text}")
                return self.booking_helper.stop_booking_process
        except Exception:
            pass

        logging.info("| Login successful")
        return self.booking_helper.continue_booking_process

    def switch_day(self) -> str:
        """Switch to the desired day for booking slots."""
        future_date, diff_week = self.booking_helper.get_day(self.days_before_bookable)
        self.day = future_date.strftime("%A")

        try:
            for _ in range(diff_week):
                self._click_button(
                    self.xpath_helper.get_xpath_booking_head() + "[3]/div[9]/div/div/i"
                )
                logging.info("| Switched to following week")

            day_button = self.booking_helper.get_day_button(self.day, self.xpath_helper)
            self._click_button(day_button)
            logging.info(f"| Switched to day: {self.day}, {future_date}")
        except Exception as e:
            logging.error(f"! Error during day switch: {e}")

    def book_class(self, class_dict: dict, booking_action: bool = True) -> None:
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
                break

            time_slot, class_slot, prioritize_waiting_list = (
                entry.get("time"),
                entry.get("class"),
                entry.get("wl"),
            )

            if not all_possible_booking_slots_dict:
                logging.info("! No class found for this day.")
                break

            button_xpath = self._get_button_xpath(
                all_possible_booking_slots_dict, time_slot, class_slot
            )
            if not button_xpath:
                continue

            if self._book_class_slot(
                button_xpath, class_slot, time_slot, prioritize_waiting_list
            ):
                break

    def _input_text(self, xpath: str, text: str) -> None:
        WebDriverWait(self.driver, 20).until(
            exco.element_to_be_clickable((By.XPATH, xpath))
        ).send_keys(text)

    def _click_button(self, xpath: str) -> None:
        WebDriverWait(self.driver, 20).until(
            exco.element_to_be_clickable((By.XPATH, xpath))
        ).click()

    def _load_and_transform_input_class_dict(self) -> list:
        """Load and transform the input class_dict into a list of unique class entries."""
        return list({entry.get("class") for entry in self.class_dict})

    def _get_all_bounding_boxes_in_window(self) -> list:
        """Get all bounding boxes containing booking slots present in the current window."""
        WebDriverWait(self.driver, 20).until(
            exco.element_to_be_clickable(
                (By.XPATH, self.xpath_helper.get_xpath_booking_head())
            )
        )
        return self.driver.find_elements(
            By.XPATH, self.xpath_helper.get_xpath_booking_head()
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
                textfield = self.driver.find_element(By.XPATH, xpath_test).text
                if textfield in class_entry_list:
                    time_slot = self.driver.find_element(
                        By.XPATH,
                        f"{self.xpath_helper.get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]",
                    ).text
                    logging.info(f"- Time: {time_slot} - Class: {textfield}")

                    xpath_button_book = self.xpath_helper.get_xpath_booking_slot(
                        booking_slot=slot_index, book_action=self.booking_action
                    )
                    all_possible_booking_slots_dict[textfield].append(
                        {
                            time_slot: {
                                "textfield": textfield,
                                "time_slot": time_slot,
                                "slot_index": slot_index,
                                "xpath": xpath_button_book,
                            }
                        }
                    )
            except NoSuchElementException:
                continue
        return all_possible_booking_slots_dict

    def _get_button_xpath(
        self, all_possible_booking_slots_dict: dict, time_slot: str, class_slot: str
    ) -> str:
        """Get the XPath of the button for booking a class slot."""
        try:
            all_possible_booking_slots_dict_flatten = {
                k: v
                for d in all_possible_booking_slots_dict.get(class_slot, [])
                for k, v in d.items()
            }
            button_xpath = all_possible_booking_slots_dict_flatten.get(
                time_slot, {}
            ).get("xpath")
            logging.info(f"? Checking {class_slot} at {time_slot}...")
            return button_xpath
        except (AttributeError, TypeError):
            logging.info(
                f"! No class of type {class_slot} is present on {self.day} at {time_slot}"
            )
            return None

    def _book_class_slot(
        self,
        button_xpath: str,
        class_slot: str,
        time_slot: str,
        prioritize_waiting_list: bool,
    ) -> bool:
        """Book a specific class slot."""
        logging.info(f"| Booking {class_slot} at {time_slot}")

        self._click_book_button(button_xpath)

        alert_obj = self.warning_prompt_helper.alert_is_present(self.driver)
        if alert_obj:
            return self.warning_prompt_helper.evaluate_alert(
                alert_obj, prioritize_waiting_list
            )

        error_text = self.warning_prompt_helper.evaluate_alert(self.driver)
        if error_text:
            return self.warning_prompt_helper.evaluate_alert(error_text)

        logging.info("! Class booked")
        return self.booking_helper.stop_booking_process()

    def _click_book_button(self, xpath_button_book: str) -> None:
        """Click the book button using JavaScript execution."""
        element = self.driver.find_element(By.XPATH, xpath_button_book)
        while True:
            current_time = datetime.now().time().strftime("%H:%M:%S.%f")
            if current_time >= self.execution_booking_time:
                start_time = datetime.now()
                logging.info(f"| Start execution at {current_time}")
                self.driver.execute_script("arguments[0].click();", element)
                end_time = datetime.now()
                logging.info(f"| Executed at {end_time.time()}")
                logging.info(f"| Took {(end_time - start_time).total_seconds()}s")
                break

    def _check_login_alert(self) -> str:
        """Check for alert messages after login."""
        try:
            alert_div = WebDriverWait(self.driver, 10).until(
                exco.presence_of_element_located(
                    (
                        By.XPATH,
                        self.xpath_helper.get_xpath_login_error_window(),
                    )  #  "/html/body/div/div[2]/div/div"
                )
            )
            return alert_div.text
        except NoSuchElementException:
            return ""
