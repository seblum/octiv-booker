import os
from datetime import date, timedelta
from src.slotbooker.xpaths import XPathHelper


class EnvVarNotSetError(Exception):
    """Custom exception to be raised when an environment variable is not set."""

    pass


class ClassVarHelper:
    def __init__(self, var_names):
        """
        Initialize the helper with a list of environment variable names to check.

        :param var_names: List of environment variable names.
        """
        self.var_names = var_names

    def check_vars(self):
        """
        Check if the environment variables are set. Raises an exception if any are not set.

        :raises EnvVarNotSetError: If any environment variable is not set.
        """
        for var_name in self.var_names:
            if var_name in os.environ:
                print(f"The environment variable '{var_name}' is set.")
            else:
                print(f"The environment variable '{var_name}' is not set.")
                raise EnvVarNotSetError(
                    f"Required environment variable '{var_name}' is not set."
                )


def stop_booking_process() -> bool:
    """Determine whether to stop the booking process of slots.

    Returns:
        bool: True if further bookings should be stopped, False if new bookings can continue.
    """
    return True


def get_day(days_before_bookable: int) -> tuple[date, int]:
    """Checks and selects which day will be selected,
    based on how many days from today shall be selected.

    Args:
        days_before_bookable (int): Number of days to go in the future

    Returns:
        tuple[date, int]: Future day to be selected, number of different calendar weeks
    """
    today = date.today()
    future_date = today + timedelta(days=days_before_bookable)
    today_calendar_week = today.isocalendar().week
    future_calendar_week = future_date.isocalendar().week
    diff_week = future_calendar_week - today_calendar_week

    return future_date, diff_week


def get_day_button(day_to_book: str, xpath_helper: XPathHelper) -> str:
    """Sets the XPath of the button of the day to be clicked.

    Args:
        day_to_book (str): The weekday to be selected

    Returns:
        str: XPath of the button of the corresponding weekday
    """
    day_indices = {
        "Monday": 2,
        "Tuesday": 3,
        "Wednesday": 4,
        "Thursday": 5,
        "Friday": 6,
        "Saturday": 7,
        "Sunday": 8,
    }
    return xpath_helper.get_day_button_xpath(day_indices.get(day_to_book, 0))


def get_booking_slot(
    booking_slot: int, book_action: bool, xpath_helper: XPathHelper
) -> str:
    """Sets the XPath of the booking slot button to be clicked and whether
    the slot (class) shall be booked or cancelled.

    Args:
        booking_slot (int): Number of the booking slot
        book_action (bool): True if action shall be booked, False if canceled.

    Returns:
        str: XPath of the booking slot button to be clicked
    """
    return xpath_helper.get_xpath_booking_slot(booking_slot, book_action)
