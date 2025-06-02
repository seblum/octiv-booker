import unittest
from datetime import date, timedelta
from slotbooker.utils.helpers import (
    stop_booking_process,
    get_day,
)
from slotbooker.utils.xpaths import XPath


class TestXPathHelper(unittest.TestCase):
    def test_xpath_booking_head(self):
        self.assertEqual(XPath.booking_section_head(), "/html/body/div/div[6]/div/div")

    def test_xpath_login_username_input(self):
        self.assertEqual(
            XPath.login_username_input(),
            "/html/body/div/div[3]/div/div/div/div/div/div/form/div[1]/input",
        )

    def test_xpath_login_password_input(self):
        self.assertEqual(
            XPath.login_password_input(),
            "/html/body/div/div[3]/div/div/div/div/div/div/form/div[2]/input",
        )

    def test_xpath_login_error_window(self):
        self.assertEqual(
            XPath.login_error_window(),
            "/html/body/div/div[2]/div/div",
        )

    def test_get_day_button_xpath(self):
        self.assertEqual(
            XPath.weekday_button(3),
            "/html/body/div/div[6]/div/div[3]/div[0]/div/p",
        )

    def test_xpath_enter_slot(self):
        self.assertEqual(
            XPath.enter_slot(1),
            "/html/body/div/div[6]/div/div[1]/div/div[1]/div[3]/button",
        )
        self.assertEqual(
            XPath.cancel_slot(1),
            "/html/body/div/div[6]/div/div[1]/div/div[2]/div[3]/button",
        )

    def test_xpath_error_window(self):
        self.assertEqual(
            XPath.error_window(),
            "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]",
        )

    def test_xpath_error_text_window(self):
        self.assertEqual(
            XPath.error_text_window(),
            "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[2]",
        )


class TestBookingHelper(unittest.TestCase):
    def test_get_day(self):
        today = date.today()
        future_date, diff_week = get_day(5)
        self.assertEqual(future_date, today + timedelta(days=5))
        self.assertEqual(
            diff_week, (future_date.isocalendar().week - today.isocalendar().week)
        )

    def test_get_day_button(self):
        self.assertEqual(
            XPath.weekday_button("Monday"),
            "/html/body/div/div[6]/div/div[3]/div[2]/div/p",
        )
        self.assertEqual(
            XPath.weekday_button("Sunday"),
            "/html/body/div/div[6]/div/div[3]/div[8]/div/p",
        )
        self.assertEqual(
            XPath.weekday_button("NonexistentDay"),
            "/html/body/div/div[6]/div/div[3]/div[0]/div/p",
        )

    def test_stop_booking_process(self):
        self.assertTrue(stop_booking_process())


if __name__ == "__main__":
    unittest.main()
