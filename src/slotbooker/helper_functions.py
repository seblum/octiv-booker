from datetime import date, timedelta

def get_xpath_booking_head() -> str:
    """Head of the XPath of the booking table page after log in.

    Returns:
        str: Head of XPath of booking table
    """
    return "/html/body/div/div[6]/div/div"

def get_xpath_login_username_head() -> str:
    """Head of the XPath of the login page where the username is set.

    Returns:
        str: Head of XPath of username login page
    """
    return "/html/body/div/div[3]/div/div/div/div/div/div/form"

def get_xpath_login_password_head() -> str:
    """Head of the XPath of the login page where the password is set
    and the terms and agreements have to be checked.

    Returns:
        str: Head of XPath of username password page
    """
    return "/html/body/div[1]/div[3]/div/div/div/div/div/div/form"

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

def get_day_button(day_to_book: str) -> str:
    """Sets the XPath of the button of the day to be clicked.

    Args:
        day_to_book (str): The weekday to be selected

    Returns:
        str: XPath of the button of the corresponding weekday
    """

    def __get_xpath_button(day_index: int) -> str:
        return f"{get_xpath_booking_head()}[3]/div[{day_index}]/div/p"

    # Monday=2, Sunday=8
    day_buttons = {
        "Monday": __get_xpath_button(2),
        "Tuesday": __get_xpath_button(3),
        "Wednesday": __get_xpath_button(4),
        "Thursday": __get_xpath_button(5),
        "Friday": __get_xpath_button(6),
        "Saturday": __get_xpath_button(7),
        "Sunday": __get_xpath_button(8),
    }

    return day_buttons.get(day_to_book, "")

def get_booking_slot(booking_slot: int, book_action: bool) -> str:
    """Sets the XPath of the booking slot button to be clicked and whether
    the slot (class) shall be booked or cancelled.

    Args:
        booking_slot (int): Number of the booking slot
        book_action (bool): True if action shall be booked, False if canceled.

    Returns:
        str: XPath of the booking slot button to be clicked
    """

    def _get_xpath_book(slot: int) -> str:
        return f"{get_xpath_booking_head()}[{slot}]/div/div[1]/div[3]/button"

    def _get_xpath_cancel(slot: int) -> str:
        return f"{get_xpath_booking_head()}[{slot}]/div/div[2]/div[3]/button"

    return _get_xpath_book(booking_slot) if book_action else _get_xpath_cancel(booking_slot)

def get_error_window() -> str:
    """Get the XPath of the error message within the booking page.

    Returns:
        str: XPath of the error message element within the HTML structure.
    """
    return "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]"
         # "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]" # for normal
         # "/html/body/div/div[2]/div/div/div[1]/div" # for login

def get_error_text_window() -> str:
    """Get the XPath of the error text message within the booking page.

    Returns:
        str: XPath of the element containing the detailed error text within the HTML structure.
    """
    return "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[2]"

def continue_bookings() -> bool:
    """Determine whether to continue booking other slots.

    Returns:
        bool: True if new bookings should be continued, False if further bookings should be stopped.
    """
    return False

def stop_booking_process() -> bool:
    """Determine whether to stop the booking process of slots.

    Returns:
        bool: True if further bookings should be stopped, False if new bookings can continue.
    """
    return True
