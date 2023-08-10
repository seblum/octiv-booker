from enum import Enum
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .helper_functions import get_error_window, get_error_text_window


class AlertTypes(Enum):
    """
    Enumeration of possible alert types that can be encountered.
    """

    ClassFull = "Die Stunde ist voll. Möchtest du auf die Warteliste kommen? Du wirst automatisch gebucht, wenn ein Platz frei wird."
    CancelBooking = "Möchtest du deine Buchung wirklich stornieren?"
    CannotBookInAdvance = "You cannot book this far in advance"
    MaxBookings = "You have reached your maximum bookings per day limit"
    NotIdentifyAlertError = "Could not identify Error/Alert"
    NotError = "No Error present"
    NotAlert = "No Alert present"


def alert_is_present(driver) -> object:
    """
    Checks if an alert is present and returns the alert object.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        object: The alert object if present, else None.
    """
    try:
        WebDriverWait(driver, 3).until(
            EC.alert_is_present(),
            "Timed out waiting for PA creation " + "confirmation popup to appear.",
        )
        logging.info("! Alert present")
        alert_obj = driver.switch_to.alert
        return alert_obj
    except TimeoutException:
        logging.info(f"| {AlertTypes.NotAlert.value}")
        # self.driver.find_element(By.NAME, 'Error')

    return None


def get_alert_type(alert_obj: object) -> Enum:
    """
    Determines the type of alert based on its text.

    Args:
        alert_obj: The alert object.

    Returns:
        Enum: The AlertTypes enum corresponding to the detected alert type.
    """
    alert_text = alert_obj.text
    if any([x.lower() in alert_text.lower() for x in ["waiting list", "Warteliste"]]):
        logging.info("! Class full")
        alert_check = AlertTypes.ClassFull
    elif any(
        [
            x.lower() in alert_text.lower()
            for x in ["wirklich", "stornieren", "stornieren?"]
        ]
    ):
        alert_check = AlertTypes.MaxBookings
    else:
        alert_check = AlertTypes.NotIdentifyAlertError
    return alert_check


def error_is_present(driver) -> str:
    """
    Checks if an error is present and returns the error text.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        str: The error text if present, else an empty string.
    """
    try:
        driver.find_element(By.XPATH, get_error_window())
        logging.info("! Error !")
        error_text = driver.find_element(By.XPATH, get_error_text_window()).text
        return error_text
    except NoSuchElementException:
        return None


def evaluate_error(error_text) -> bool:
    """
    Evaluates the error text and determines if it matches certain conditions.

    Args:
        error_text: The error text to evaluate.

    Returns:
        bool: True if the error matches specific conditions, else False.
    """
    match error_text:
        case AlertTypes.MaxBookings.value:
            logging.info(f"! {AlertTypes.MaxBookings.value}")
            return True
        case AlertTypes.CannotBookInAdvance.value:
            logging.info(f"! {AlertTypes.CannotBookInAdvance.value}")
            return True
        case _:
            logging.info(f"! {AlertTypes.NotIdentifyAlertError.value}")
            return False
