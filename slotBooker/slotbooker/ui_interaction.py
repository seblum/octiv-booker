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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

    def __init__(self, driver: object, base_url: str, days_before_bookable: int):
        self.driver = driver
        self.base_url = base_url
        self.days_before_bookable = days_before_bookable
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


    def book_class(self, class_dict: dict, booking_action: bool = True) -> None:
        def __load_and_transform_input_class_dict() -> list:
            self.class_dict = class_dict.get(self.day)
            class_entry_list = list(set([entry.get("class") for entry in self.class_dict]))
            return class_entry_list

        def __get_all_bounding_boxes_in_window() -> object:
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
            print(f"? possible classes for '{class_entry_list}'")

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
                        all_possible_booking_slots_dict[textfield].append(tmp_dict)
                except NoSuchElementException:
                    continue
            return all_possible_booking_slots_dict

        def __click_book_button(xpath_button_book: str) -> None:
            # Use execute_script() when another element is covering the element to be clicked
            element = self.driver.find_element(By.XPATH, xpath_button_book)
            self.driver.execute_script("arguments[0].click();", element)

        def __booking_waiting_list(
            prioritize_waiting_list: str, alert_obj: object
        ) -> bool:
            match prioritize_waiting_list:
                case True:
                    print("! Booking waiting list...")
                    alert_obj.accept()
                    print(colored("| Waiting list booked", "blue"))
                    return True # end program
                case _:
                    print(
                        f"! Parameter 'wl' is set to {prioritize_waiting_list} \n> Skipping waiting list..."
                    )
                    alert_obj.dismiss()
                    print("> Looking for further slots...")
                    return False # continue

        def __abort_canceling_slot(
            alert_obj: object
        ) -> bool:
            print(
                f"! Aborted canceling slot..."
            )
            alert_obj.dismiss()
            print("> Looking for further slots...")
            return False  # continue

        def __book_class_slot(button_xpath: str) -> bool:
            print(
                f"{colored('| Booking', 'blue')} {class_slot} {colored('at', 'blue')} {time_slot}"
            )
            __click_book_button(xpath_button_book=button_xpath)

            # Check whether alert appears
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
                    # currently not necessarily needed as canceling class is not listed in all_possible_booking_slots_dict
                    case AlertTypes.CancelBooking:
                        ret = __abort_canceling_slot
                        return ret
                    case _:
                        print(AlertTypes.NotIdentifyAlertError.value)

            error_text = error_is_present(self.driver)
            if error_text is None:
                print(f"| {AlertTypes.NotAlertError.value}r")
            else:
                return evaluate_error(error_text)

            print(colored("! Class booked", "green"))
            return True

        #
        # ACTUAL CODE OF FUNCTION
        #
        self.booking_action = booking_action

        all_slots_bounding_boxes = __get_all_bounding_boxes_in_window()
        class_entry_list = __load_and_transform_input_class_dict()

        resultsdict = __get_all_bounding_boxes_by_class_name(
            class_entry_list=class_entry_list, all_slots_bounding_boxes=all_slots_bounding_boxes
        )

        for entry in self.class_dict:
            if entry.get("class") == "None":
                print("No class set for this day.")
                break
            else:
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

                if __book_class_slot(button_xpath):
                    break
