import time
from xml.dom.minidom import Element
from termcolor import colored

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


class Booker:
    def __init__(self,driver: object,base_url:str,days_before_bookable:int):
        self.driver = driver
        self.base_url=base_url
        self.days_before_bookable=days_before_bookable
        self.class_list=None
        self.booking_action=None
        self.day = None


    def get_driver(self):
        return self.driver
    
    def login(self, username: str, password: str) -> None:
        """Log in onto website

        Args:
            driver (object): Webdriver, currently Chromium
            base_url (str): URL of the website to be logged in to
            username (str): username for login
            password (str): password for login
        """
        self.driver.get(self.base_url)
        # needs initial time to wait, could be reduced
        time.sleep(4)
        # username field
        self.driver.find_element(By.XPATH, f"{get_xpath_login_username_head()}/div[1]/input").send_keys(username)
        self.driver.find_element(By.XPATH, f"{get_xpath_login_username_head()}/button").send_keys(Keys.RETURN)
        print(colored('| submit user name successful', 'blue'))

        # password field
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"{get_xpath_login_password_head()}/div[2]/input"))
        ).send_keys(password)
        # checkbox
        self.driver.find_element(By.XPATH, f"{get_xpath_login_password_head()}/div[3]/div/div/div[1]/div/i").click()
        # submit
        self.driver.find_element(By.XPATH, f"{get_xpath_login_password_head()}/button").send_keys(Keys.RETURN)
        print(colored('| login successful', 'blue'))


    def switch_day(self) -> str:
        """Switches to the day where a class shall be booked.

        Args:
            driver (object): Webdriver, currently Chromium
            days_before_bookable (int): Number of days to go in the future
            booking_action (bool, optional): True if action shall be booked, False if canceled. Defaults to True.

        Returns:
            str: Weekday that have been switched to
        """
        day, next_week = get_day(self.days_before_bookable)

        if next_week:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f"{get_xpath_booking_head()}[3]/div[9]/div/div/i"))
            ).click()
            print("| switched to next week")

        day_button = get_day_button(day)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, day_button))).click()

        print(colored('| switched to day:', 'blue'),f"{day}")
        self.day = day


    def book_slot(self, class_list: list, booking_action: bool = True) -> None:
        """Book/Cancel the slot of the class. The function gets all possible booking slots and
            selects those who match the class_name. If there are multiple options, it selects the latest one

        Args:
            driver (object): Webdriver, currently Chromium
            class_name (str): Name of the class to be attended, e.g. "Gymnastics"
            booking_action (bool, optional): True if action shall be booked, False if canceled. Defaults to True.
        """
        # /div/div[?]/div[2]/p[1] the XPath of the booking slot bounding boxes changes depending on
        # whether there has been a booking or not. 1 if not yet booked, 2 if already has been booked
        self.class_list = class_list.get(self.day)
        self.booking_action = booking_action
                
        bounding_box_number_by_action = 1 if booking_action else 2

        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, get_xpath_booking_head())))
        all_slots_bounding_boxes = self.driver.find_elements(By.XPATH, get_xpath_booking_head())

        #print(class_list)

        entry_list = list(set([entry.get("class") for entry in self.class_list]))      

        # Iterate over all found bounding boxes
        print(f"? possible classes for '{entry_list}'")
        class_slots, time_slots = [], []
        resultsdict, tmp = {}, {}
        for slot_index in range(len(all_slots_bounding_boxes)):
            slot_index += 1
            xpath_test = f"{get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[2]/p[1]"
            try:
                textfield = self.driver.find_element(By.XPATH, xpath_test).text
                if textfield in entry_list:
                    # get the corresponding time slot and print it
                    xpath_time_slot = (
                        f"{get_xpath_booking_head()}[{slot_index}]/div/div[{bounding_box_number_by_action}]/div[1]/p[1]"
                    )
                    time_slot = self.driver.find_element(By.XPATH, xpath_time_slot).text
                    print(f"- time: {time_slot} - class: {textfield} - index: {slot_index}")
                    # append index of class to list
                    class_slots.append(slot_index)
                    time_slots.append(time_slot)
                    xpath_button_book = get_booking_slot(booking_slot=slot_index, book_action=booking_action)
                    #print(xpath_button_book)
                    tmp[time_slot] = {"textfield":textfield,"time_slot":time_slot,"slot_index":slot_index,"xpath": xpath_button_book}
                    resultsdict[textfield] = tmp
                    
            except:
                continue
        #print(resultsdict)

        def _click_book_button(xpath_button_book: str) -> None:
            # book max slot: if list contains multiple elements, then last element

            # Use execute_script() when another element is covering the element to be clicked
            element = self.driver.find_element(By.XPATH, xpath_button_book)
            self.driver.execute_script("arguments[0].click();", element)

        for entry in self.class_list:
            #print(entry)
            # try:
            time_slot = entry.get("time")
            class_nr = entry.get("class")
            prioritize_waiting_list = entry.get("wl")
            #print(prioritize_waiting_list)
            try:
                print(f"| Checking {class_nr} at {time_slot}...")
                tmp_bottin = resultsdict.get(entry.get("class")).get(entry.get("time")).get("xpath")
                # could check extra if already booked and need to check for cancel button
            except AttributeError:
                # results in NoneType 
                print(f"{colored('! It is likely that no class of type', 'red')} {class_nr} {colored('is present on', 'red')} {self.day} {time_slot} {colored('(results in NoneType)', 'red')}")

                #print(f"! It's likely that no class of type {class_nr} is present on {self.day} {time_slot}. \n (results in NoneType)")
                continue
            #print(tmp_bottin)
            if booking_action:
                print(f"{colored('| Booking', 'blue')} {class_nr} {colored('at', 'blue')} {time_slot}")

                _click_book_button(xpath_button_book=tmp_bottin)
                # TODO: Check whether I can a 200 return to check whether successful

                try:
                    WebDriverWait(self.driver, 3).until(EC.alert_is_present(),
                                                'Timed out waiting for PA creation ' +
                                                'confirmation popup to appear.')
                    print(colored('! Alert present', 'red'))
                    alert_obj = self.driver.switch_to.alert
                    print("! Class full")
                    #print(alert_obj.text)
                    if prioritize_waiting_list == True:
                        print("! Booking waiting list...")
                        alert_obj.accept()
                        print(colored('| Waiting list booked', 'blue'))
                        break   # end program
                    else:
                        print("! Skipping waiting list...")
                        alert_obj.dismiss()
                        print("| Looking for further slots...")
                        # continue
                    time.sleep(1)
                except TimeoutException:
                    print(colored('! No alert | Class booked', 'green'))

            else:
                print(f"| Cancelling {class_nr} at {time_slot}")
                _click_book_button(xpath_button_book=tmp_bottin)
                time.sleep(5)
                print(f"! Class cancelled")
            # except:
            #     continue
