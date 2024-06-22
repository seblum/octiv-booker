from datetime import date, timedelta


class XPathHelper:
    """Helper class to generate XPath strings for various elements on the page."""

    def __init__(self):
        self.booking_head = "/html/body/div/div[6]/div/div"
        self.login_username_head = "/html/body/div/div[3]/div/div/div/div/div/div/form"
        self.login_password_head = (
            "/html/body/div[1]/div[3]/div/div/div/div/div/div/form"
        )
        self.login_error_window = "/html/body/div/div[2]/div/div"
        self.error_window_path = (
            "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]"
        )
        self.error_text_window_path = (
            "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[2]"
        )

    def get_xpath_booking_head(self) -> str:
        return self.booking_head

    def get_xpath_login_username_head(self) -> str:
        return self.login_username_head

    def get_xpath_login_password_head(self) -> str:
        return self.login_password_head

    def get_xpath_login_error_window(self) -> str:
        return self.login_error_window

    def get_day_button_xpath(self, day_index: int) -> str:
        return f"{self.booking_head}[3]/div[{day_index}]/div/p"

    def get_xpath_booking_slot(self, slot: int, book_action: bool) -> str:
        if book_action:
            return f"{self.booking_head}[{slot}]/div/div[1]/div[3]/button"
        else:
            return f"{self.booking_head}[{slot}]/div/div[2]/div[3]/button"

    def get_xpath_error_window(self) -> str:
        return self.error_window_path

    def get_xpath_error_text_window(self) -> str:
        return self.error_text_window_path


class BookingHelper:
    """Helper class for booking and login operations."""

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def continue_booking_process() -> bool:
        """Determine whether to continue booking other slots.

        Returns:
            bool: True if new bookings should be continued, False if further bookings should be stopped.
        """
        return False

    @staticmethod
    def stop_booking_process() -> bool:
        """Determine whether to stop the booking process of slots.

        Returns:
            bool: True if further bookings should be stopped, False if new bookings can continue.
        """
        return True
