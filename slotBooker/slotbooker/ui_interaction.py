import logging
from collections import defaultdict
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from .helper_functions import (
    get_booking_slot,
    get_day,
    get_day_button,
    get_xpath_booking_head,
    get_xpath_login_password_head,
    get_xpath_login_username_head,
    continue_bookings, 
    stop_booking_process
)

from .alerts_and_errors import (
    alert_is_present,
    evaluate_alert,
    error_is_present,
    evaluate_error,
    AlertTypes,
)


class Booker:
    """
    A class representing a booking agent for Octiv.

    Attributes:
        driver (object): The Selenium WebDriver instance.
        base_url (str): The base URL of the booking website.
        days_before_bookable (int): Number of days before a class becomes bookable.
        execution_booking_time (str): time the booking is executed
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

    Note:
        This class provides methods for logging in, switching days, and booking classes on a specific website.
    """

    def __init__(self, driver: object, base_url: str, days_before_bookable: int, execution_booking_time: str):
        self.driver = driver
        self.base_url = base_url
        self.days_before_bookable = days_before_bookable
        self.execution_booking_time = execution_booking_time
        self.class_dict = None
        self.booking_action = None
        self.day = None

    def login(self, username: str, password: str) -> None:
        """Login to the booking website using the provided credentials.

        Args:
            username (str): The user's username for login.
            password (str): The user's password for login.

        Returns:
            None: This function does not return anything.

        Note:
            This function logs into the website and prints confirmation messages.

        Raises:
            TimeoutException: If the login process times out.
        """
        self.driver.get(self.base_url)

        # username field
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"{get_xpath_login_username_head()}/div[1]/input")
            )
        ).send_keys(username)
        self.driver.find_element(
            By.XPATH, f"{get_xpath_login_username_head()}/button"
        ).send_keys(Keys.RETURN)
        logging.info("| submit user name successful")

        # password field
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"{get_xpath_login_password_head()}/div[2]/input")
            )
        ).send_keys(password)
        # checkbox
        self.driver.find_element(
            By.XPATH, f"{get_xpath_login_password_head()}/div[3]/div/div/div[1]/div/i"
        ).click()
        # submit
        self.driver.find_element(
            By.XPATH, f"{get_xpath_login_password_head()}/button"
        ).send_keys(Keys.RETURN)
        logging.info("| login successful")

    def switch_day(self) -> str:
        """Switch to the desired day for booking slots.

        Returns:
            str: The selected day for booking.

        Note:
            This function switches to the desired day and prints confirmation messages.

        Raises:
            TimeoutException: If the day switch process times out.
        """
        future_date, diff_week = get_day(self.days_before_bookable)
        day = future_date.strftime("%A")
        if diff_week > 0:
            while diff_week > 0:
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"{get_xpath_booking_head()}[3]/div[9]/div/div/i")
                    )
                ).click()
                logging.info("| switched to following week")
                diff_week -= 1

        day_button = get_day_button(day)
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, day_button))
        ).click()

        logging.info(f"| switched to day: {day}, {future_date}")
        self.day = day

    def book_class(self, class_dict: dict, booking_action: bool = True) -> None:
        """
        Book classes based on provided booking information.

        Args:
            class_dict (dict): Dictionary containing class booking information for a specific day.
            booking_action (bool, optional): Indicates whether to perform booking actions (True) or not (False). Default is True.

        Returns:
            None: This function does not return anything.

        Note:
            This function iterates through class information and performs booking actions based on provided data.

        Raises:
            Various exceptions related to Selenium interactions.
        """

        def __load_and_transform_input_class_dict() -> list:
            """
            Load and transform the input class_dict into a list of unique class entries.

            Returns:
                list: A list of unique class entries.

            Note:
                This function retrieves the class_dict entry for the selected day and extracts unique class entries.
            """
            self.class_dict = class_dict.get(self.day)
            class_entry_list = list(
                set([entry.get("class") for entry in self.class_dict])
            )
            return class_entry_list

        def __get_all_bounding_boxes_in_window() -> object:
            """
            Get all bounding boxes containing booking slots present in the current window.

            Returns:
                object: A list of WebElements representing the bounding boxes.

            Note:
                This function uses Selenium to find all booking slot bounding boxes in the current window.
            """
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, get_xpath_booking_head()))
            )
            all_slots_bounding_boxes = self.driver.find_elements(
                By.XPATH, get_xpath_booking_head()
            )
            return all_slots_bounding_boxes

        def __get_all_bounding_boxes_by_class_name(
            class_entry_list: list, all_slots_bounding_boxes: list
        ) -> dict:
            """
            Get all possible booking slots for specified class entries and bounding boxes.

            Args:
                class_entry_list (list): List of unique class entries.
                all_slots_bounding_boxes (list): List of WebElements representing bounding boxes.

            Returns:
                dict: A dictionary containing possible booking slots for each class entry.

            Note:
                This function iterates through bounding boxes, identifies valid booking slots, and records relevant data.
            """
            logging.info(f"? possible classes for '{class_entry_list}'")

            # /div/div[?]/div[2]/p[1] the XPath of the booking slot bounding boxes changes depending on
            # whether there has been a booking or not. 1 if not yet booked, 2 if already has been booked
            bounding_box_number_by_action = 1 if self.booking_action else 2

            all_possible_booking_slots_dict = defaultdict(list)
            # Iterate over all found bounding boxes
            for slot_index in range(len(all_slots_bounding_boxes)):
                slot_index += 1
                xpath_test = f"{get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
                try:
                    textfield = self.driver.find_element(By.XPATH, xpath_test).text
                    if textfield in class_entry_list:
                        # get the corresponding time slot and print it
                        xpath_time_slot = f"{get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                        time_slot = self.driver.find_element(
                            By.XPATH, xpath_time_slot
                        ).text
                        logging.info(f"- time: {time_slot} - class: {textfield}")
                        # append index of class to list
                        xpath_button_book = get_booking_slot(
                            booking_slot=slot_index, book_action=booking_action
                        )
                        tmp_dict = {}
                        tmp_dict[time_slot] = {
                            "textfield": textfield,
                            "time_slot": time_slot,
                            "slot_index": slot_index,
                            "xpath": xpath_button_book,
                        }
                        all_possible_booking_slots_dict[textfield].append(tmp_dict)
                except NoSuchElementException:
                    continue
            return all_possible_booking_slots_dict

        def __click_book_button(xpath_button_book: str) -> None:
            """
            Click the book button using JavaScript execution.

            Args:
                xpath_button_book (str): XPath of the book button.

            Returns:
                None: This function does not return anything.

            Note:
                This function uses JavaScript execution to click the book button in cases where it may be covered.
            """
            # Use execute_script() when another element is covering the element to be clicked
            element = self.driver.find_element(By.XPATH, xpath_button_book)
            
            while True:
                if datetime.now().time().strftime("%H:%M:%S.%f") >= self.execution_booking_time:
                    start_time = datetime.now()
                    logging.info(f"| Start execution at {datetime.now().time()}")
                    self.driver.execute_script("arguments[0].click();", element)
                    end_time = datetime.now()
                    logging.info(f"| Executed at {end_time.time()}")
                    logging.info(f"| Took {(end_time - start_time)}s - Ideal start time: {(end_time-(end_time - start_time)).time()}")
                    break



        def __book_class_slot(button_xpath: str) -> bool:
            """
            Book a specific class slot.

            Args:
                button_xpath (str): XPath of the book button.

            Returns:
                bool: True if class is successfully booked, False if not.

            Note:
                This function attempts to book a class slot, handling alerts and errors.
            """
            logging.info(f"| Booking {class_slot} at {time_slot}")
            
            __click_book_button(xpath_button_book=button_xpath)

            # Check whether alert appears
            alert_obj = alert_is_present(self.driver)
            if alert_obj is None:
                logging.info(f"| {AlertTypes.NotAlert.value}")
            else:
                return evaluate_alert(alert_obj,prioritize_waiting_list)

            error_text = error_is_present(self.driver)
            if error_text is None:
                logging.info(f"| {AlertTypes.NotError.value}")
            else:
                return evaluate_error(error_text) # returns False to continue bookings

            logging.info("! Class booked")
            return stop_booking_process()

        #
        # ACTUAL CODE OF FUNCTION
        #
        logging.info(f"| Execution starts at >= {self.execution_booking_time}")
        self.booking_action = booking_action

        all_slots_bounding_boxes = __get_all_bounding_boxes_in_window()
        class_entry_list = __load_and_transform_input_class_dict()

        all_possible_booking_slots_dict = __get_all_bounding_boxes_by_class_name(
            class_entry_list=class_entry_list,
            all_slots_bounding_boxes=all_slots_bounding_boxes,
        )

        for entry in self.class_dict:
            if entry.get("class") == "None":
                logging.info("! No class set for this day.")
                break
            elif not all_possible_booking_slots_dict: # dict is empty
                logging.info("! No class found for this day.")
                break
            else:
                time_slot, class_slot, prioritize_waiting_list = (
                    entry.get("time"),
                    entry.get("class"),
                    entry.get("wl"),
                )
                all_possible_booking_slots_dict_flatten = {
                    k: v for d in all_possible_booking_slots_dict.get(class_slot) for k, v in d.items()
                }
                try:
                    # try getting an xpath for the given time and class. could also be an if-else statement
                    logging.info(f"? Checking {class_slot} at {time_slot}...")
                    button_xpath = all_possible_booking_slots_dict_flatten.get(time_slot).get("xpath")
                    # could check extra if already booked and need to check for cancel button
                except AttributeError:
                    # results in NoneType
                    logging.info(
                        f"! It is likely that no class of type {class_slot} is present on {self.day} {time_slot} (results in NoneType)"
                    )
                    continue

                if __book_class_slot(button_xpath):
                    break
