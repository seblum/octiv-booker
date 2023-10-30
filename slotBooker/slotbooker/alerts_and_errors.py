from enum import Enum
import logging
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .helper_functions import get_error_window, get_error_text_window, continue_bookings, stop_booking_process


class AlertTypes(Enum):
    """
    Enumeration of possible alert types that can be encountered.
    """
    ClassFull = "Class is fully booked"
    ClassFullGerman = "Die Stunde ist voll. Möchtest du auf die Warteliste kommen? Du wirst automatisch gebucht, wenn ein Platz frei wird."
    CancelBooking = "Möchtest du deine Buchung wirklich stornieren?"
    CannotBookInAdvance = "You cannot book this far in advance"
    MaxBookings = "You have reached your maximum bookings per day limit"
    NotIdentifyAlert = "Could not identify Alert"
    NotIdentifyError = "Could not identify Error"
    NotAlert = "No Alert present"
    NotError = "No Error present"


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
        pass
        # logging.info(f"| {AlertTypes.NotAlert.value}")
        # self.driver.find_element(By.NAME, 'Error')

    return None


def evaluate_alert(alert_obj: object, prioritize_waiting_list: Any) -> Enum:
    """
    Determines the type of alert based on its text.

    Args:
        alert_obj (object): The alert object.
        prioritize_waiting_list (): 
    Returns:
        Enum: The AlertTypes enum corresponding to the detected alert type.
    """
    alert_text = alert_obj.text
    if any([x.lower() in alert_text.lower() for x in ["waiting list", "Warteliste"]]):

        logging.info("! Class full")
        ret = _alert_waiting_list_booking(
                prioritize_waiting_list=prioritize_waiting_list,
                alert_obj=alert_obj,
            )
        return ret
    elif any(
        [
            x.lower() in alert_text.lower()
            for x in ["wirklich", "stornieren", "stornieren?"]
        ]
    ):
        ret = _alert_cancel_slot(alert_obj)
        return ret
    else:
        logging.info(AlertTypes.NotIdentifyAlert.value)
        logging.info(f"! Alert message: {alert_obj.text}")
        return continue_bookings()


def _alert_waiting_list_booking(prioritize_waiting_list: str, alert_obj: object
) -> bool:
    """
    Handle booking waiting list option in the alert.

    Args:
        prioritize_waiting_list (str): Indicates whether to prioritize the waiting list (True) or not (False).
        alert_obj (object): The alert object.

    Returns:
        bool: True if program should end, False if it should continue.

    Note:
        This function handles the waiting list booking option in the alert dialog.
    """
    match prioritize_waiting_list:
        case True:
            logging.info("! Booking waiting list...")
            alert_obj.accept()
            logging.info("| Waiting list booked")
            return stop_booking_process()  # end program
        case _:
            logging.info(
                f"! Parameter 'wl' is set to {prioritize_waiting_list} > Skipping waiting list"
            )
            alert_obj.dismiss()
            logging.info("> Looking for further slots...")
            return continue_bookings()  # continue


def _alert_cancel_slot(alert_obj: object) -> bool:
    """
    Handle aborting the canceling of a slot.

    Args:
        alert_obj (object): The alert object.

    Returns:
        bool: False to continue searching for further slots.

    Note:
        This function handles the situation when slot cancelation is aborted.
    """
    logging.info(f"! Aborted canceling slot...")
    alert_obj.dismiss()
    logging.info("> Looking for further slots...")
    return continue_bookings()  # continue


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
        case AlertTypes.ClassFull.value:
            logging.info(f"! {AlertTypes.ClassFull.value}")
            return False
        case _:
            logging.info(f"! {AlertTypes.NotIdentifyError.value}")
            logging.info(f"! Error message: {error_text}")
            return False
