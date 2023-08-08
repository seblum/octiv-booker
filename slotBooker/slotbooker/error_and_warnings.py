from termcolor import colored
from enum import Enum

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


class AlertTypes(Enum):
    """Enumeration of Alert Types for Slotbooker.

    This enumeration represents different types of alerts that can be raised during the slot booking process
    in the Slotbooker application.

    Attributes:
        ClassFull (str): Alert indicating that the class is already full and cannot be booked.
        MaxBookings (str): Alert indicating that the maximum number of bookings for the class has been reached.
        NoAlert (str): Indicating that no alert is present.

    Example:
        To use the AlertTypes enumeration, access the attributes as follows:

        >>> alert_type = AlertTypes.ClassFull
        >>> if alert_type == AlertTypes.ClassFull:
        ...     print("The class is already full.")
        ...
        The class is already full.
    """

    ClassFull = "class_full"
    CancelBooking = "stornieren"
    CannotBookInAdvance = "You cannot book this far in advance"
    MaxBookings = "You have reached your maximum bookings per day limit"
    NoAlert = "none"


def alert_is_present(driver) -> object:
    """Check if an alert is present on the website.

    Returns:
        object: The alert object if present, None otherwise.

    Note:
        This function checks for the presence of an alert and returns the alert object if found.
    """
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
    """Determine the type of the alert based on its text.

    Args:
        alert_obj (object): The alert object.

    Returns:
        Enum: An enumeration value indicating the type of alert.

    Note:
        This function analyzes the alert's text and returns the corresponding AlertTypes enumeration value.
    """
    alert_text = alert_obj.text
    if any([x.lower() in alert_text.lower() for x in ["waiting list", "Warteliste"]]):
        print("! Class full")
        alert_check = AlertTypes.ClassFull
    elif any([x.lower() in alert_text.lower() for x in ["wirklich", "stornieren"]]):
        alert_check = AlertTypes.MaxBookings
    else:
        alert_check = AlertTypes.NoAlert
    return alert_check


def error_is_present(driver) -> str:
    error_path = "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]"
    error_text_path = "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[2]"
    if driver.find_element(By.XPATH, error_path):
        print(colored("! Error", "red") + "...")
        error_text = driver.find_element(By.XPATH, error_text_path).text
    else:
        error_text = "| no error"
    return error_text


def evaluate_error(error_text) -> bool:
    match error_text:
        case AlertTypes.MaxBookings.value:
            print(colored(error_text, "red"))
            return True
        case AlertTypes.CannotBookInAdvance.value:
            print(colored(error_text, "red"))
            return True
        case _:
            print("Could not identify error")
            return True
