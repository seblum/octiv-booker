# from calendar import weekday
# from datetime import date
# from pickle import NONE
# from xml.etree.ElementPath import xpath_tokenizer

# from selenium import webdriver
# from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .helper_functions import (
    _get_xpath_booking_head,
    _get_xpath_login_password_head,
    _get_xpath_login_username_head,
    get_booking_slot,
    get_day,
    get_day_button,
)


def login(driver: object, base_url: str, username: str, password: str) -> None:
    """Log in onto website

    Args:
        driver (object): Webdriver, currently Chromium
        base_url (str): URL of the website to be logged in to
        username (str): username for login
        password (str): password for login
    """
    print(">")
    driver.get(base_url)

    # username field
    driver.find_element(By.XPATH, f"{_get_xpath_login_username_head()}/div[1]/input").send_keys(username)
    driver.find_element(By.XPATH, f"{_get_xpath_login_username_head()}/button").send_keys(Keys.RETURN)
    print("| submit user name successful")

    # password field
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"{_get_xpath_login_password_head()}/div[2]/input"))
    ).send_keys(password)
    # checkbox
    driver.find_element(By.XPATH, f"{_get_xpath_login_password_head()}/div[3]/div/div/div[1]/div/i").click()
    # submit
    driver.find_element(By.XPATH, f"{_get_xpath_login_password_head()}/button").send_keys(Keys.RETURN)
    print("| login successful")


def switch_day(driver: object, days_before_bookable: int, booking_action: bool = True) -> str:
    """Switches to the day where a class shall be booked.

    Args:
        driver (object): Webdriver, currently Chromium
        days_before_bookable (int): Number of days to go in the future
        booking_action (bool, optional): True if action shall be booked, False if canceled. Defaults to True.

    Returns:
        str: Weekday that have been switched to
    """
    day, next_week = get_day(days_before_bookable)

    if next_week:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"{_get_xpath_booking_head()}[3]/div[9]/div/div/i"))
        ).click()
        print("|-- switched to next week")

    day_button = get_day_button(day)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, day_button))).click()

    print(f"  | switch to {day} successful")
    return day


def book_slot(driver: object, class_name: str, booking_action: bool = True) -> None:
    """Book the slot of the class

    Args:
        driver (object): Webdriver, currently Chromium
        class_name (str): Name of the class to be attended, e.g. "Gymnastics"
        booking_action (bool, optional): True if action shall be booked, False if canceled. Defaults to True.
    """
    # /div/div[?]/div[2]/p[1] the XPath of the booking slot bounding boxes changes depending on
    # whether there has been a booking or not. 1 if not yet booked, 2 if already has been booked
    bounding_box_number_by_action = 1 if booking_action else 2

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, _get_xpath_booking_head())))
    all_slots_bounding_boxes = driver.find_elements(By.XPATH, _get_xpath_booking_head())

    # Iterate over all found bounding boxes
    print(f"  ? possible bookings for '{class_name}'")
    class_slot = []
    for i in range(len(all_slots_bounding_boxes)):
        xpath_test = f"{_get_xpath_booking_head()}[{i}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
        try:
            # If the bounding box is one relevant for booking a class and has the relevant class name
            if driver.find_element(By.XPATH, xpath_test).text == class_name:
                # get the corresponding time slot and print it
                xpath_time_slot = (
                    f"{_get_xpath_booking_head()}[{i}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                )
                print(f"- time: {driver.find_element(By.XPATH, xpath_time_slot).text} - index: {i}")
                # append index of class to list
                class_slot.append(i)
        except:
            continue

    # TODO: build in popup for cancel class
    if class_slot:
        # try:
        # book max slot: if list contains multiple elements, then last element
        xpath_button_book = get_booking_slot(booking_slot=max(class_slot), book_action=booking_action)
        WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, xpath_button_book))).click()
        # except UnexpectedAlertPresentException:
        #   print("cannot cancel, popup detected")
    else:
        print("  ! No bookable slot found")
