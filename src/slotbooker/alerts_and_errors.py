from enum import Enum
import logging
from typing import Any, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .helper_functions import get_error_window, get_error_text_window, continue_bookings, stop_booking_process

class AlertTypes(Enum):
    """Enumeration of possible alert types that can be encountered."""
    ClassFull = "Class is fully booked"
    ClassFullGerman = "Die Stunde ist voll. Möchtest du auf die Warteliste kommen? Du wirst automatisch gebucht, wenn ein Platz frei wird."
    CancelBooking = "Möchtest du deine Buchung wirklich stornieren?"
    CannotBookInAdvance = "You cannot book this far in advance"
    MaxBookings = "You have reached your maximum bookings per day limit"
    NotIdentifyAlert = "Could not identify Alert"
    NotIdentifyError = "Could not identify Error"
    NotAlert = "No Alert"
    NotError = "No Error"

def alert_is_present(driver) -> Optional[object]:
    """Checks if an alert is present and returns the alert object.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        Optional[object]: The alert object if present, else None.
    """
    try:
        WebDriverWait(driver, 3).until(
            EC.alert_is_present(),
            "Timed out waiting for alert to appear.",
        )
        logging.info("! Alert present")
        return driver.switch_to.alert
    except TimeoutException:
        return None

def evaluate_alert(alert_obj: object, prioritize_waiting_list: Any) -> Enum:
    """Determines the type of alert based on its text.

    Args:
        alert_obj (object): The alert object.
        prioritize_waiting_list (Any): Indicates whether to prioritize the waiting list (True) or not (False).

    Returns:
        Enum: The AlertTypes enum corresponding to the detected alert type.
    """
    alert_text = alert_obj.text
    if any(keyword.lower() in alert_text.lower() for keyword in ["waiting list", "Warteliste"]):
        logging.info("! Class full")
        return _handle_waiting_list_booking(prioritize_waiting_list, alert_obj)
    elif any(keyword.lower() in alert_text.lower() for keyword in ["wirklich", "stornieren", "stornieren?"]):
        return _handle_cancel_slot(alert_obj)
    else:
        logging.info(AlertTypes.NotIdentifyAlert.value)
        logging.info(f"! Alert message: {alert_text}")
        return continue_bookings()

def _handle_waiting_list_booking(prioritize_waiting_list: str, alert_obj: object) -> bool:
    """Handle booking waiting list option in the alert.

    Args:
        prioritize_waiting_list (str): Indicates whether to prioritize the waiting list (True) or not (False).
        alert_obj (object): The alert object.

    Returns:
        bool: True if program should end, False if it should continue.
    """
    if prioritize_waiting_list:
        logging.info("! Booking waiting list...")
        alert_obj.accept()
        logging.info("| Waiting list booked")
        return stop_booking_process()
    else:
        logging.info(f"! Parameter 'wl' is set to {prioritize_waiting_list} > Skipping waiting list")
        alert_obj.dismiss()
        logging.info("> Looking for further slots...")
        return continue_bookings()

def _handle_cancel_slot(alert_obj: object) -> bool:
    """Handle aborting the canceling of a slot.

    Args:
        alert_obj (object): The alert object.

    Returns:
        bool: False to continue searching for further slots.
    """
    logging.info("! Aborted canceling slot...")
    alert_obj.dismiss()
    logging.info("> Looking for further slots...")
    return continue_bookings()

def error_is_present(driver) -> Optional[str]:
    """Checks if an error is present and returns the error text.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        Optional[str]: The error text if present, else None.
    """
    try:
        driver.find_element(By.XPATH, get_error_window())
        logging.info("! Error !")
        error_text = driver.find_element(By.XPATH, get_error_text_window()).text
        return error_text
    except NoSuchElementException:
        return None

def evaluate_error(error_text: str) -> bool:
    """Evaluates the error text and determines if it matches certain conditions.

    Args:
        error_text (str): The error text to evaluate.

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
        case AlertTypes.ClassFull.value:
            logging.info(f"! {AlertTypes.ClassFull.value}")
            return False
        case _:
            logging.info(f"! {AlertTypes.NotIdentifyError.value}")
            logging.info(f"! Error message: {error_text}")
            return False