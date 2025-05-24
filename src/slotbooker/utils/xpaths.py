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
