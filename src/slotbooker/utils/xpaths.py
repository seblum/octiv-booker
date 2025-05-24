from enum import Enum


class XPathEnum(str, Enum):
    """Enum for commonly used XPath strings."""

    BOOKING_HEAD = "/html/body/div/div[6]/div/div"

    # Username XPaths
    LOGIN_USERNAME_INPUT = (
        "/html/body/div/div[3]/div/div/div/div/div/div/form/div[1]/input"
    )
    LOGIN_USERNAME_BUTTON = "/html/body/div/div[3]/div/div/div/div/div/div/form/button"

    # Password XPaths
    LOGIN_PASSWORD_INPUT = (
        "/html/body/div[1]/div[3]/div/div/div/div/div/div/form/div[2]/input"
    )
    LOGIN_PASSWORD_CHECK = "/html/body/div[1]/div[3]/div/div/div/div/div/div/form/div[3]/div/div/div[1]/div/i"
    LOGIN_PASSWORD_BUTTON = (
        "/html/body/div[1]/div[3]/div/div/div/div/div/div/form/button"
    )

    LOGIN_ERROR_WINDOW = "/html/body/div/div[2]/div/div"
    ERROR_WINDOW_PATH = "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]"
    ERROR_TEXT_WINDOW_PATH = "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[2]"
    GET_DAY_BUTTON = "/html/body/div/div[6]/div/div[3]/div[{day_index}]/div/p"
    BOOK_SLOT_ACTION = "/html/body/div/div[6]/div/div[{slot}]/div/div[1]/div[3]/button"
    CANCEL_SLOT_ACTION = (
        "/html/body/div/div[6]/div/div[{slot}]/div/div[2]/div[3]/button"
    )


class XPath:
    """Helper class with static methods for XPath generation."""

    @staticmethod
    def booking_head() -> str:
        return XPathEnum.BOOKING_HEAD.value

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

    @staticmethod
    def get_day_button_xpath(day_index: int) -> str:
        return XPathEnum.GET_DAY_BUTTON.value.format(day_index=day_index)
        # f"{XPathEnum.BOOKING_HEAD.value}[3]/div[{day_index}]/div/p"

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
