from datetime import date


def _get_xpath_booking_head() -> str:
    """Head of the XPath of the booking table page after log in

    Returns:
        str: Head of XPath of booking table
    """
    return "/html/body/div/div[5]/div/div"


def _get_xpath_login_username_head() -> str:
    """Head of XPath of the login page where the username is set

    Returns:
        str: Head of XPath of username login page
    """
    return "/html/body/div/div[3]/div/div/div/div/div/div/form"


def _get_xpath_login_password_head() -> str:
    """Head of XPath of the login page where the password is set
        and the terms and agreements have to be checked.

    Returns:
        str: Head of XPath of username password page
    """
    return "/html/body/div[1]/div[3]/div/div/div/div/div/div/form"


def get_day(days_before_bookable: int) -> tuple[str, bool]:
    """Checks and selects which day will be selected,
    based on how many days from today shall be selected

    Args:
        days_before_bookable (int): Number of days to go in the future

    Returns:
        tuple[str, bool]: weekday to be selected, True if weekday is in the next week
    """
    week_days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    today = date.today().weekday()
    future_day = today + days_before_bookable
    if future_day < 7:
        return week_days[future_day], False
    else:
        future_day = future_day - 7
        return week_days[future_day], True


def get_day_button(day_to_book: str) -> str:
    """Sets the XPath of the button of the day to be clicked

    Args:
        day_to_book (str): The weekday to be selected

    Returns:
        str: XPath of the button of the corresponding weekday
    """

    def _get_xpath_button(day_index: int) -> str:
        return f"/html/body/div/div[5]/div/div[3]/div[{day_index}]/div/p"

    # monday=2, sunday=8
    match day_to_book:
        case "Monday":
            day_button = _get_xpath_button(2)
        case "Tuesday":
            day_button = _get_xpath_button(3)
        case "Wednesday":
            day_button = _get_xpath_button(4)
        case "Thursday":
            day_button = _get_xpath_button(5)
        case "Friday":
            day_button = _get_xpath_button(6)
        case "Saturday":
            day_button = _get_xpath_button(7)
        case "Sunday":
            day_button = _get_xpath_button(8)
    return day_button


def get_booking_slot(booking_slot: int, book_action: bool) -> str:
    """sets the XPath of the booking slot button to be clicked and whether
        the slot (class) shall be booked or cancelled

    Args:
        booking_slot (int): Number of the booking slot
        book_action (bool): True if action shall be booked, False if canceled.

    Returns:
        str: XPath of the booking slot button to be clicked
    """

    def _get_xpath_book(slot: int) -> str:
        return f"{_get_xpath_booking_head()}[{slot}]/div/div[1]/div[3]/button"

    def _get_xpath_cancel(slot: int) -> str:
        return f"{_get_xpath_booking_head()}[{slot}]/div/div[2]/div[3]/button"

    return _get_xpath_book(booking_slot) if book_action else _get_xpath_cancel(booking_slot)
