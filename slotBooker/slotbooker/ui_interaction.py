import time
from xml.dom.minidom import Element
from termcolor import colored
from collections import defaultdict
from enum import Enum

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


from .helper_functions import (
    get_booking_slot,
    get_day,
    get_day_button,
    get_xpath_booking_head,
    get_xpath_login_password_head,
    get_xpath_login_username_head,
)

from .error_and_warnings import (
    alert_is_present,
    get_alert_type,
    error_is_present,
    evaluate_error,
    AlertTypes,
)


class Booker:
    """Slotbooker's main booking functionality.

    This class handles the slot booking process in the Slotbooker application. It uses a Selenium web driver
    to interact with the booking website. The class provides methods for login, switching to the desired day,
    and booking/canceling slots for specific classes.

    Args:
        driver (object): The Selenium web driver to interact with the website.
        base_url (str): The base URL of the booking website.
        days_before_bookable (int): The number of days in advance for which classes can be booked.

    Attributes:
        driver (object): The Selenium web driver used to interact with the website.
        base_url (str): The base URL of the booking website.
        days_before_bookable (int): The number of days in advance for which classes can be booked.
        class_list (list): A list of dictionaries containing class information for the day to be booked.
        booking_action (bool): A flag indicating whether the booking action is enabled (True) or canceling (False).
        day (str): The day for which the slots are being booked.

    Note:
        The 'booking_action' attribute determines whether the slots should be booked (True) or canceled (False).

    Example:
        Create a 'Booker' object with the required parameters and use its methods for booking slots:

        >>> driver = get_driver(chromedriver=config.get("chromedriver"))
        >>> booker = Booker(
        ...     driver=driver,
        ...     days_before_bookable=config.get("days_before_bookable"),
        ...     base_url=config.get("base_url"),
        ... )
        >>> booker.login(username="your_username", password="your_password")
        >>> booker.switch_day()
        >>> class_list = [
        ...     {"time": "08:00", "class": "Yoga", "wl": False},
        ...     {"time": "12:00", "class": "Pilates", "wl": True},
        ... ]
        >>> booker.book_class(class_list=class_list, booking_action=True)
    """

    def __init__(self, driver: object, base_url: str, days_before_bookable: int):
        self.driver = driver
        self.base_url = base_url
        self.days_before_bookable = days_before_bookable
        self.class_list = None
        self.booking_action = None
        self.day = None
        self.close_booking = False

    def __get_driver(self):
        """Get the Selenium web driver.

        Returns:
            object: The Selenium web driver.
        """
        return self.driver

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

        # TODO: use EC.element_to_be_clickable() rather than sleep
        # needs initial time to wait, could be reduced
        time.sleep(4)

        # username field
        self.driver.find_element(
            By.XPATH, f"{get_xpath_login_username_head()}/div[1]/input"
        ).send_keys(username)
        self.driver.find_element(
            By.XPATH, f"{get_xpath_login_username_head()}/button"
        ).send_keys(Keys.RETURN)
        print(colored("| submit user name successful", "blue"))

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
        print(colored("| login successful", "blue"))

    def switch_day(self) -> str:
        """Switch to the desired day for booking slots.

        Returns:
            str: The selected day for booking.

        Note:
            This function switches to the desired day and prints confirmation messages.

        Raises:
            TimeoutException: If the day switch process times out.
        """
        day, next_week = get_day(self.days_before_bookable)
        if next_week:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"{get_xpath_booking_head()}[3]/div[9]/div/div/i")
                )
            ).click()
            print("| switched to next week")

        day_button = get_day_button(day)
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, day_button))
        ).click()

        print(colored("| switched to day:", "blue"), f"{day}")
        self.day = day

    def book_class(self, class_list: list, booking_action: bool = True) -> None:
        """Book or cancel the slots for the specified classes.

        Args:
            class_list (list): A list of dictionaries containing class information to be booked/canceled.
            booking_action (bool, optional): A flag indicating whether to book (True) or cancel (False) slots.
                                            Defaults to True (booking action).

        Returns:
            None: This function does not return anything.

        Note:
            This function iterates through the provided 'class_list' and interacts with the website to either book or
            cancel the slots for the specified classes. It prints the progress and confirmation messages during the process.

        Raises:
            AttributeError: If class information is missing for a specific day or time.

        Nested Functions:
            The 'book_class' function contains several nested helper functions for interacting with the website:
            - __get_all_bounding_boxes(entry_list, all_slots_bounding_boxes, bounding_box_number_by_action)
            -> Gets all bounding boxes for possible booking slots based on class information.
            - __click_book_button(xpath_button_book) -> Clicks on the booking button for the specified slot.
            - __alert_is_present() -> Checks if an alert is present on the website.
            - __get_alert_type(alert_obj) -> Determines the type of the alert based on its text.
            - __booking_waiting_list(prioritize_waiting_list, alert_obj) -> Handles booking the waiting list if prioritized.
            - __book_class_slot(button_xpath) -> Books a slot for the specified class and time.
        """

        def __get_all_bounding_boxes_in_window(
            entry_list: list,
            all_slots_bounding_boxes: list,
            bounding_box_number_by_action: int,
        ) -> dict:
            """Get all bounding boxes for possible booking slots.

            Args:
                entry_list (list): A list of class names to search for.
                all_slots_bounding_boxes (list): A list of all found bounding boxes on the website.
                bounding_box_number_by_action (int): The number of the bounding box to use (1 or 2).

            Returns:
                dict: A dictionary containing the class information and corresponding XPaths for booking.

            Note:
                This function iterates through the found bounding boxes, identifies the class and time slot,
                and stores the relevant information along with the booking XPath.
            """

            print(f"? possible classes for '{entry_list}'")

            resultsdict = defaultdict(list)
            # Iterate over all found bounding boxes
            for slot_index in range(len(all_slots_bounding_boxes)):
                slot_index += 1
                xpath_test = f"{get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
                try:
                    textfield = self.driver.find_element(By.XPATH, xpath_test).text
                    if textfield in entry_list:
                        # get the corresponding time slot and print it
                        xpath_time_slot = f"{get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                        time_slot = self.driver.find_element(
                            By.XPATH, xpath_time_slot
                        ).text
                        print(
                            f"- time: {time_slot} - class: {textfield} - index: {slot_index}"
                        )
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
                        resultsdict[textfield].append(tmp_dict)
                except:
                    continue
            return resultsdict

        def __click_book_button(xpath_button_book: str) -> None:
            """Click the booking button for the specified slot.

            Args:
                xpath_button_book (str): The XPath of the booking button.

            Returns:
                None: This function does not return anything.

            Note:
                This function clicks on the booking button using JavaScript to handle overlapping elements if needed.
            """

            # TODO: Use execute_script() when another element is covering the element to be clicked
            element = self.driver.find_element(By.XPATH, xpath_button_book)
            self.driver.execute_script("arguments[0].click();", element)

        def __booking_waiting_list(
            prioritize_waiting_list: str, alert_obj: object
        ) -> bool:
            """Handle booking the waiting list if prioritized.

            Args:
                prioritize_waiting_list (str): Flag indicating whether to prioritize waiting list booking.
                alert_obj (object): The alert object.

            Returns:
                bool: True if the waiting list is booked (ends program), False otherwise (continue searching).

            Note:
                This function handles the booking of the waiting list based on the 'prioritize_waiting_list' flag.
            """
            match prioritize_waiting_list:
                case True:
                    print("! Booking waiting list...")
                    alert_obj.accept()
                    print(colored("| Waiting list booked", "blue"))
                    return True  # end program
                case _:
                    print(
                        f"! Parameter 'wl' is set to {prioritize_waiting_list} \n> Skipping waiting list..."
                    )
                    alert_obj.dismiss()
                    print("> Looking for further slots...")
                    return False  # continue

        def __book_class_slot(button_xpath: str) -> bool:
            """Book a slot for the specified class and time.

            Args:
                button_xpath (str): The XPath of the booking button.

            Returns:
                bool: True if the class slot is successfully booked, False otherwise.

            Note:
                This function books a slot for the specified class and time. It also handles alerts and waiting list booking.
            """
            print(
                f"{colored('| Booking', 'blue')} {class_slot} {colored('at', 'blue')} {time_slot}"
            )
            __click_book_button(xpath_button_book=button_xpath)

            # Check whether alert appears
            # TODO: currently only checks alerts that are full bookings
            # no already booked on day
            alert_obj = alert_is_present(self.driver)
            if alert_obj is not None:
                alert_check = get_alert_type(alert_obj)

                match alert_check:
                    case AlertTypes.ClassFull:
                        ret = __booking_waiting_list(
                            prioritize_waiting_list=prioritize_waiting_list,
                            alert_obj=alert_obj,
                        )
                        return ret
                    # case AlertTypes.CancelBooking:
                    #     continue
                    # TODO: dismiss canceln booking
                    case _:
                        print("Could not identify alert")

            error_text = error_is_present(self.driver)
            if error_text is not None:
                return evaluate_error(error_text)
            else:
                print("| No Error")

            print(colored("! Class booked", "green"))
            return True

        # /div/div[?]/div[2]/p[1] the XPath of the booking slot bounding boxes changes depending on
        # whether there has been a booking or not. 1 if not yet booked, 2 if already has been booked
        self.class_list = class_list.get(self.day)
        self.booking_action = booking_action

        bounding_box_number_by_action = 1 if booking_action else 2

        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, get_xpath_booking_head()))
        )
        all_slots_bounding_boxes = self.driver.find_elements(
            By.XPATH, get_xpath_booking_head()
        )

        entry_list = list(set([entry.get("class") for entry in self.class_list]))
        resultsdict = __get_all_bounding_boxes_in_window(
            entry_list=entry_list,
            all_slots_bounding_boxes=all_slots_bounding_boxes,
            bounding_box_number_by_action=bounding_box_number_by_action,
        )

        for entry in self.class_list:
            if entry.get("class") == "None":
                print("No class set for this day.")
                break
            time_slot, class_slot, prioritize_waiting_list = (
                entry.get("time"),
                entry.get("class"),
                entry.get("wl"),
            )
            resultsdict_flatten = {
                k: v for d in resultsdict.get(class_slot) for k, v in d.items()
            }
            try:
                # try getting an xpath for the given time and class. could also be an if-else statement
                print(f"| Checking {class_slot} at {time_slot}...")
                button_xpath = resultsdict_flatten.get(time_slot).get("xpath")
                # could check extra if already booked and need to check for cancel button
            except AttributeError:
                # results in NoneType
                print(
                    f"{colored('! It is likely that no class of type', 'red')} {class_slot} {colored('is present on', 'red')} {self.day} {time_slot} {colored('(results in NoneType)', 'red')}"
                )
                continue

            if booking_action:
                self.close_booking = __book_class_slot(button_xpath)
                if self.close_booking:
                    break
            else:
                print(f"| Cancelling {class_slot} at {time_slot}")
                __click_book_button(xpath_button_book=button_xpath)
                time.sleep(5)
                print(f"! Class cancelled")
