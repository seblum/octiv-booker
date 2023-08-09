from termcolor import colored
from enum import Enum

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .helper_functions import get_error_window, get_error_text_window


class AlertTypes(Enum):
    ClassFull = "Die Stunde ist voll. Möchtest du auf die Warteliste kommen? Du wirst automatisch gebucht, wenn ein Platz frei wird."
    CancelBooking = "Möchtest du deine Buchung wirklich stornieren?"
    CannotBookInAdvance = "! You cannot book this far in advance"
    MaxBookings = "! You have reached your maximum bookings per day limit"
    NotIdentifyAlertError = "! Could not identify Error/Alert"
    NotAlertError = "! No Error/Alert present"


def alert_is_present(driver) -> object:
    try:
        WebDriverWait(driver, 3).until(
            EC.alert_is_present(),
            "Timed out waiting for PA creation " + "confirmation popup to appear.",
        )
        print(colored("! Alert present", "red"))
        alert_obj = driver.switch_to.alert
        return alert_obj
    except TimeoutException:
        print("| No Alert")
        # self.driver.find_element(By.NAME, 'Error')

    return None


def get_alert_type(alert_obj: object) -> Enum:
    alert_text = alert_obj.text
    if any([x.lower() in alert_text.lower() for x in ["waiting list", "Warteliste"]]):
        print("! Class full")
        alert_check = AlertTypes.ClassFull
    elif any([x.lower() in alert_text.lower() for x in ["wirklich", "stornieren", "stornieren?"]]):
        alert_check = AlertTypes.MaxBookings
    else:
        alert_check = AlertTypes.NotIdentifyAlertError
    return alert_check


def error_is_present(driver) -> str:
    if driver.find_element(By.XPATH, get_error_window()):
        print(colored("! Error", "red") + "...")
        error_text = driver.find_element(By.XPATH, get_error_text_window()).text
    return error_text


def evaluate_error(error_text) -> bool:
    match error_text:
        case AlertTypes.MaxBookings.value:
            print(colored(AlertTypes.MaxBookings.value, "red"))
            return True
        case AlertTypes.CannotBookInAdvance.value:
            print(colored(AlertTypes.CannotBookInAdvance.value, "red"))
            return True
        case _:
            print(AlertTypes.NotIdentifyAlertError.value)
            return True
