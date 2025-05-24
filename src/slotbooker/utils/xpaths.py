from enum import Enum


class XPathEnum(str, Enum):
    """Enum for commonly used XPath strings."""

    # Base paths
    BASE = "/html/body/div"
    LOGIN_SECTION = f"{BASE}/div[3]/div/div/div/div/div/div/form"
    ERROR_SECTION = f"{BASE}/div[2]/div/div"
    BOOKING_SECTION = f"{BASE}/div[6]/div/div"

    # Login - Username
    LOGIN_USERNAME_INPUT = f"{LOGIN_SECTION}/div[1]/input"
    LOGIN_USERNAME_BUTTON = f"{LOGIN_SECTION}/button"

    # Login - Password
    LOGIN_PASSWORD_INPUT = f"{LOGIN_SECTION}/div[2]/input"
    LOGIN_PASSWORD_CHECK = f"{LOGIN_SECTION}/div[3]/div/div/div[1]/div/i"
    LOGIN_PASSWORD_BUTTON = f"{LOGIN_SECTION}/button"

    # Error handling
    LOGIN_ERROR_WINDOW = ERROR_SECTION
    ERROR_WINDOW_PATH = f"{ERROR_SECTION}/div[1]/div/div/div[2]/p[1]"
    ERROR_TEXT_WINDOW_PATH = f"{ERROR_SECTION}/div[1]/div/div/div[2]/p[2]"

    # Booking
    SWITCH_WEEK_BUTTON = f"{BOOKING_SECTION}[3]/div[9]/div/div/i"
    GET_DAY_BUTTON = f"{BOOKING_SECTION}[3]/div[{{day_index}}]/div/p"
    BOOK_SLOT_ACTION = f"{BOOKING_SECTION}[{{slot}}]/div/div[1]/div[3]/button"
    CANCEL_SLOT_ACTION = f"{BOOKING_SECTION}[{{slot}}]/div/div[2]/div[3]/button"


class XPath:
    """Helper class with static methods for XPath generation."""

    @staticmethod
    def booking_section_head() -> str:
        return XPathEnum.BOOKING_SECTION.value

    # Username XPaths
    @staticmethod
    def login_username_input() -> str:
        return XPathEnum.LOGIN_USERNAME_INPUT.value

    @staticmethod
    def login_username_button() -> str:
        return XPathEnum.LOGIN_USERNAME_BUTTON.value

    # Password XPaths
    @staticmethod
    def login_password_input() -> str:
        return XPathEnum.LOGIN_PASSWORD_INPUT.value

    @staticmethod
    def login_password_check() -> str:
        return XPathEnum.LOGIN_PASSWORD_CHECK.value

    @staticmethod
    def login_password_button() -> str:
        return XPathEnum.LOGIN_PASSWORD_BUTTON.value

    @staticmethod
    def login_error_window() -> str:
        return XPathEnum.LOGIN_ERROR_WINDOW.value

    # Switch week button
    @staticmethod
    def switch_week_button() -> str:
        return XPathEnum.SWITCH_WEEK_BUTTON.value

    @staticmethod
    def weekday_button(day_to_book: int) -> str:
        day_indices = {
            "Monday": 2,
            "Tuesday": 3,
            "Wednesday": 4,
            "Thursday": 5,
            "Friday": 6,
            "Saturday": 7,
            "Sunday": 8,
        }
        return XPathEnum.GET_DAY_BUTTON.value.format(
            day_index=day_indices.get(day_to_book, 0)
        )

    @staticmethod
    def booking_slot_action(slot: int) -> str:
        return XPathEnum.BOOK_SLOT_ACTION.value.format(slot=slot)

    @staticmethod
    def cancel_slot_action(slot: int) -> str:
        return XPathEnum.CANCEL_SLOT_ACTION.value.format(slot=slot)

    # @staticmethod
    # def booking_slot(slot: int, book_action: bool) -> str:
    #     if book_action:
    #         return f"{XPathEnum.BOOKING_HEAD.value}[{slot}]/div/div[1]/div[3]/button"
    #     else:
    #         return f"{XPathEnum.BOOKING_HEAD.value}[{slot}]/div/div[2]/div[3]/button"

    @staticmethod
    def error_window() -> str:
        return XPathEnum.ERROR_WINDOW_PATH.value

    @staticmethod
    def error_text_window() -> str:
        return XPathEnum.ERROR_TEXT_WINDOW_PATH.value
