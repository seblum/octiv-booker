from calendar import weekday
from datetime import date
from pickle import NONE
from xml.etree.ElementPath import xpath_tokenizer

from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
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
    driver.get(base_url)

    # username field
    driver.find_element(By.XPATH, f"{_get_xpath_login_username_head()}/div[1]/input").send_keys(username)
    driver.find_element(By.XPATH, f"{_get_xpath_login_username_head()}/button").send_keys(Keys.RETURN)
    print("> submit user name successful")

    # password field
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"{_get_xpath_login_password_head()}/div[2]/input"))
    ).send_keys(password)
    # checkbox
    driver.find_element(By.XPATH, f"{_get_xpath_login_password_head()}/div[3]/div/div/div[1]/div/i").click()
    # submit
    driver.find_element(By.XPATH, f"{_get_xpath_login_password_head()}/button").send_keys(Keys.RETURN)
    print("> login successful")


def switch_day(driver: object, days_before_bookable: int, booking_action: bool = True) -> str:
    day, next_week = get_day(days_before_bookable)

    if next_week:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"{_get_xpath_booking_head()}[3]/div[9]/div/div/i"))
        ).click()
        print("- switched to next week")

    day_button = get_day_button(day)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, day_button))).click()

    print(f"> switch to {day} successful")
    return day


def book_slot(driver: object, class_name: str, book_action: bool = True) -> None:
    # get all slots of the day

    # /div/div[1]/div[2]/p[1] wenn noch nichts gebucht
    # /div/div[2]/div[2]/p[1] wenn bereits gebucht
    bounding_box_number_by_action = 1 if book_action else 2

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, _get_xpath_booking_head())))
    my_elements = driver.find_elements(By.XPATH, _get_xpath_booking_head())

    def _get_slots_by_class(class_name: str) -> list:
        print(f"? possible bookings for '{class_name}'")
        ls = []
        for i in range(len(my_elements)):
            xpath_test = f"{_get_xpath_booking_head()}[{i}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
            try:
                if driver.find_element(By.XPATH, xpath_test).text == class_name:
                    time = f"{_get_xpath_booking_head()}[{i}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                    print(f"- time: {driver.find_element(By.XPATH, time).text} - index: {i}")
                    ls.append(i)
            except:
                continue
        return ls

    # get all possible slot by class
    lists = _get_slots_by_class(class_name=class_name)

    # book max slot: if list contains multiple elements, then last element
    # get button to book
    # TODO: build in popup for cancel class
    if lists:
        # try:
        xpath_button_book = get_booking_slot(booking_slot=max(lists), book_action=book_action)
        WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, xpath_button_book))).click()
        # except UnexpectedAlertPresentException:
        #   print("cannot cancel, popup detected")

    else:
        print("!- No bookable slot found")
