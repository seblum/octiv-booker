import unittest
from datetime import date, timedelta
from slotbooker.utils.helpers import XPathHelper
from slotbooker.utils.helpers import (
    stop_booking_process,
    get_day,
    get_day_button,
    get_booking_slot,
)
from slotbooker.utils.xpaths import XPath


class TestXPathHelper(unittest.TestCase):
    def test_xpath_booking_head(self):
        self.assertEqual(XPath.booking_head(), "/html/body/div/div[6]/div/div")

    def test_xpath_login_username_head(self):
        self.assertEqual(
            XPath.login_username_head(),
            "/html/body/div/div[3]/div/div/div/div/div/div/form",
        )

    def test_xpath_login_password_head(self):
        self.assertEqual(
            XPath.login_password_head(),
            "/html/body/div[1]/div[3]/div/div/div/div/div/div/form",
        )

    def test_xpath_login_error_window(self):
        self.assertEqual(
            XPath.login_error_window(),
            "/html/body/div/div[2]/div/div",
        )

    def test_get_day_button_xpath(self):
        self.assertEqual(
            XPath.helper.get_day_button_xpath(3),
            "/html/body/div/div[6]/div/div[3]/div[3]/div/p",
        )

    def test_xpath_booking_slot(self):
        self.assertEqual(
            XPath.booking_slot(1, True),
            "/html/body/div/div[6]/div/div[1]/div/div[1]/div[3]/button",
        )
        self.assertEqual(
            XPath.booking_slot(1, False),
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
    def setUp(self):
        XPath.helper = XPathHelper()

    def test_get_day(self):
        today = date.today()
        future_date, diff_week = get_day(5)
        self.assertEqual(future_date, today + timedelta(days=5))
        self.assertEqual(
            diff_week, (future_date.isocalendar().week - today.isocalendar().week)
        )

    def test_get_day_button(self):
        self.assertEqual(
            get_day_button("Monday", XPath.helper),
            "/html/body/div/div[6]/div/div[3]/div[2]/div/p",
        )
        self.assertEqual(
            get_day_button("Sunday", XPath.helper),
            "/html/body/div/div[6]/div/div[3]/div[8]/div/p",
        )
        self.assertEqual(
            get_day_button("NonexistentDay", XPath.helper),
            "/html/body/div/div[6]/div/div[3]/div[0]/div/p",
        )

    def test_get_booking_slot(self):
        self.assertEqual(
            get_booking_slot(1, True, XPath.helper),
            "/html/body/div/div[6]/div/div[1]/div/div[1]/div[3]/button",
        )
        self.assertEqual(
            get_booking_slot(1, False, XPath.helper),
            "/html/body/div/div[6]/div/div[1]/div/div[2]/div[3]/button",
        )

    def test_stop_booking_process(self):
        self.assertTrue(stop_booking_process())


if __name__ == "__main__":
    unittest.main()
