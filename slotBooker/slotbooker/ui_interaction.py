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

from .helper_functions import get_booking_slot, get_day, get_day_button


def login(driver: object, base_url: str, username: str, password: str) -> None:
    driver.get(base_url)

    # HERE GOES YOUR CUSTOMIZED INTERACTIVE LOGIN
    xpath_login_one_head = "/html/body/div/div[3]/div/div/div/div/div/div/form"
    xpath_login_two_head = "/html/body/div[1]/div[3]/div/div/div/div/div/div/form"

    # username field
    driver.find_element(By.XPATH, f"{xpath_login_one_head}/div[1]/input").send_keys(username)
    driver.find_element(By.XPATH, f"{xpath_login_one_head}/button").send_keys(Keys.RETURN)
    print("> submit user name successful")

    # password field
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"{xpath_login_two_head}/div[2]/input"))
    ).send_keys(password)
    # checkbox
    driver.find_element(By.XPATH, f"{xpath_login_two_head}/div[3]/div/div/div[1]/div/i").click()
    # submit
    driver.find_element(By.XPATH, f"{xpath_login_two_head}/button").send_keys(Keys.RETURN)
    print("> login successful")


def switch_day(driver: object, days_before_bookable: int, booking_action: bool = True) -> str:
    day, next_week = get_day(days_before_bookable)

    if next_week:
        xpath_next_week = "/html/body/div/div[5]/div/div[3]/div[9]/div/div/i"
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_next_week))).click()
        print("- switched to next week")

    day_button = get_day_button(day)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, day_button))).click()
    # driver.find_element(By.XPATH, friday_button).send_keys(Keys.RETURN)
    print(f"> switch to {day} successful")
    return day


def book_slot(driver, class_name, book_action=True) -> None:
    # get all slots of the day
    bounding_box_per_slot = "/html/body/div/div[5]/div/div"
    xpath_head = bounding_box_per_slot

    # /div/div[1]/div[2]/p[1] wenn noch nichts gebucht
    # /div/div[2]/div[2]/p[1] wenn bereits gebucht
    bounding_box_number_by_action = 1 if book_action else 2

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, bounding_box_per_slot)))
    my_elements = driver.find_elements(By.XPATH, bounding_box_per_slot)
    # print(my_elements)
    def get_slots_by_class(class_name: str):
        ls = []
        xpath_head = "/html/body/div/div[5]/div/div"
        print(f"? possible bookings for '{class_name}'")
        for i in range(len(my_elements)):
            xpath_test = f"{xpath_head}[{i}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
            try:
                if driver.find_element(By.XPATH, xpath_test).text == class_name:
                    time = f"{xpath_head}[{i}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                    print(f"- time: {driver.find_element(By.XPATH, time).text} - index: {i}")
                    ls.append(i)
            except:
                continue
        return ls

    # get all possible slot by class
    lists = get_slots_by_class(class_name=class_name)

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
