from enum import Enum
import logging
from typing import Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .helper_functions import XPathHelper, BookingHelper


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
    LoginCredentials = "The user credentials were incorrect."


class AlertErrorHandler:
    def __init__(self, driver):
        self.driver = driver
        self.xpath_helper = XPathHelper()
        self.booking_helper = BookingHelper()

    def _wait_for_element(self, condition, timeout=3, error_message=""):
        try:
            return WebDriverWait(self.driver, timeout).until(condition, error_message)
        except (TimeoutException, NoSuchElementException):
            return None

    def alert_is_present(self) -> Optional[object]:
        """Checks if an alert is present and returns the alert object."""
        alert = self._wait_for_element(
            ec.alert_is_present(),
            error_message="Timed out waiting for alert to appear.",
        )
        if alert:
            logging.warning("Alert present")
            return self.driver.switch_to.alert
        return None

    def evaluate_alert(self, alert_obj: object, prioritize_waiting_list: Any) -> Enum:
        """Determines the type of alert based on its text."""
        alert_text = alert_obj.text
        if self._contains_keywords(alert_text, ["waiting list", "Warteliste"]):
            logging.warning("Class full")
            return self._handle_waiting_list_booking(prioritize_waiting_list, alert_obj)
        elif self._contains_keywords(
            alert_text, ["wirklich", "stornieren", "stornieren?"]
        ):
            return self._handle_cancel_slot(alert_obj)
        else:
            logging.warning(f"{AlertTypes.NotIdentifyAlert.value}: {alert_text}")
            return not self.booking_helper.stop_booking_process()

    def _contains_keywords(self, text: str, keywords: list) -> bool:
        return any(keyword.lower() in text.lower() for keyword in keywords)

    def _handle_waiting_list_booking(
        self, prioritize_waiting_list: str, alert_obj: object
    ) -> bool:
        """Handle booking waiting list option in the alert."""
        if prioritize_waiting_list:
            logging.info("Booking waiting list...")
            alert_obj.accept()
            logging.info("Waiting list booked")
            return self.booking_helper.stop_booking_process()
        else:
            logging.info(
                f"Parameter 'wl' is set to {prioritize_waiting_list} > Skipping waiting list"
            )
            alert_obj.dismiss()
            logging.info("Looking for further slots...")
            # TODO: I could send an email here.
            return not self.booking_helper.stop_booking_process()

    def _handle_cancel_slot(self, alert_obj: object) -> bool:
        """Handle aborting the canceling of a slot."""
        logging.warning("Aborted canceling slot...")
        alert_obj.dismiss()
        logging.info("Looking for further slots...")
        return not self.booking_helper.stop_booking_process()

    def error_is_present(self) -> Optional[str]:
        """Checks if an error is present and returns the error text."""
        error_window = self._wait_for_element(
            ec.presence_of_element_located(
                (By.XPATH, self.xpath_helper.get_xpath_error_window())
            ),
            timeout=3,
        )
        if error_window:
            # logging.error("! Error !")
            error_text = self.driver.find_element(
                By.XPATH, self.xpath_helper.get_xpath_error_text_window()
            ).text
            return error_text
        return None

    def evaluate_error(self, error_text: str) -> bool:
        """Evaluates the error text and determines if it matches certain conditions."""
        error_map = {
            AlertTypes.MaxBookings.value: True,
            AlertTypes.CannotBookInAdvance.value: True,
            AlertTypes.ClassFull.value: False,
        }
        result = error_map.get(error_text, False)
        if result is False:
            logging.error(f"{AlertTypes.NotIdentifyError.value}: {error_text}")
        else:
            logging.error(f"Another Error occured: {error_text}")
        return result

    def login_error_is_present(self):
        alert_div = self._wait_for_element(
            ec.presence_of_element_located(
                (By.XPATH, self.xpath_helper.get_xpath_login_error_window())
            )
        )
        if alert_div:
            alert_text = alert_div.text
            if self._contains_keywords(alert_text, ["credentials", "Fehler"]):
                logging.error(f"Credentials wrong {alert_text}")
                return True
        else:
            print("Alert message is not present.")
