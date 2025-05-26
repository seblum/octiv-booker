from enum import Enum
import logging
from typing import Any
from .helpers import stop_booking_process, text_contains_list_keywords
from slotbooker.utils.xpaths import XPath
import time
from slotbooker.utils.selenium_manager import SeleniumManager


class AlertTypes(Enum):
    """Enumeration of possible alert types that can be encountered."""

    ClassFull = "Class is fully booked."
    ClassFullGerman = "Die Stunde ist voll. Möchtest du auf die Warteliste kommen? Du wirst automatisch gebucht, wenn ein Platz frei wird."
    CancelBooking = "Möchtest du deine Buchung wirklich stornieren?"
    NotIdentifyAlert = "Could not identify Alert"
    NotAlert = "No Alert"
    LoginCredentials = "The user credentials were incorrect."


class ErrorTypes(Enum):
    """Enumeration of possible error types that can be encountered."""

    NotIdentifyError = "Could not identify Error"
    NotError = "No Error"
    CannotBookInAdvance = "You cannot book this far in advance."
    MaxBookings = "You have reached your maximum bookings per day limit."


class AlertErrorHandler:
    @staticmethod
    def evaluate_alert(alert_obj: object, prioritize_waiting_list: Any) -> Enum:
        """Determines the type of alert based on its text."""
        alert_text = alert_obj.text
        if text_contains_list_keywords(alert_text, ["waiting list", "Warteliste"]):
            logging.warning("Class full")
            return AlertErrorHandler._handle_waiting_list_booking(
                prioritize_waiting_list, alert_obj
            )
        elif text_contains_list_keywords(
            alert_text, ["wirklich", "stornieren", "stornieren?"]
        ):
            logging.warning("Aborted canceling slot...")
            alert_obj.dismiss()
            logging.info("Looking for further slots...")
            return not stop_booking_process()
        else:
            logging.warning(f"{AlertTypes.NotIdentifyAlert.value}: {alert_text}")
            return not stop_booking_process()

    @staticmethod
    def _handle_waiting_list_booking(
        prioritize_waiting_list: str, alert_obj: object
    ) -> bool:
        """Handle booking waiting list option in the alert."""
        if prioritize_waiting_list:
            logging.info("Booking waiting list...")
            alert_obj.accept()
            logging.info("Waiting list booked")
            return stop_booking_process
        else:
            logging.info(
                f"Parameter 'wl' is set to {prioritize_waiting_list} > Skipping waiting list"
            )
            alert_obj.dismiss()
            logging.info("Looking for further slots...")
            # TODO: I could send an email here.
            return not stop_booking_process

    @staticmethod
    def check_login_alert(selenium_manager):
        try:
            alert_div = selenium_manager.wait_for_element(
                xpath=XPath.login_error_window(), timeout=3
            )
            if alert_div:
                logging.error("Login alert found")
                alert_text = alert_div.text
                if text_contains_list_keywords(alert_text, ["credentials", "Fehler"]):
                    logging.error(f"Credentials wrong {alert_text}")
                    return stop_booking_process()
            else:
                logging.info("No login alert found")
        except Exception as e:
            logging.error(f"! Error during login attempt: {e}")

    @staticmethod
    def check_booking_alert(
        selenium_manager: SeleniumManager, waiting_list: list
    ) -> bool:
        alert = selenium_manager.wait_for_element_alert()
        if alert:
            logging.warning("Alert present")
            alert_obj = selenium_manager.switch_to_alert()
            if alert_obj:
                evaluate_result = AlertErrorHandler.evaluate_alert(
                    alert_obj, waiting_list
                )
                if evaluate_result is False:
                    pass
                return evaluate_result

        error_window = selenium_manager.wait_for_element(
            xpath=XPath.error_window(), timeout=3
        )
        if error_window:
            # logging.error("! Error !")
            error_text = selenium_manager.find_element(
                xpath=XPath.error_text_window()
            ).text

            if error_text:
                # TODO: Remove sleep
                time.sleep(3)

                for error in ErrorTypes:
                    if error.value == error_text:
                        logging.error(f"identified: {error.value}")
                        return error
                logging.error(f"{ErrorTypes.NotIdentifyError.value}: {error_text}")
                return ErrorTypes.NotIdentifyError
