import unittest
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import TimeoutException
from slotbooker.alerts_and_errors import WarningPromptHelper, AlertTypes


class TestWarningPromptHelper(unittest.TestCase):
    def setUp(self):
        self.driver = MagicMock()
        self.warning_prompt_helper = WarningPromptHelper(self.driver)

    # @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    # def test_alert_is_present(self, mock_wait):
    #     mock_alert = MagicMock()
    #     self.driver.switch_to.alert = mock_alert
    #     mock_wait.return_value = mock_alert

    #     alert = self.warning_prompt_helper.alert_is_present()
    #     self.assertIsNotNone(alert)
    #     self.driver.switch_to.alert.assert_called_once()

    @patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        side_effect=TimeoutException,
    )
    def test_alert_is_not_present(self, mock_wait):
        alert = self.warning_prompt_helper.alert_is_present()
        self.assertIsNone(alert)

    def test_evaluate_alert_class_full(self):
        mock_alert = MagicMock()
        mock_alert.text = "This class is full. Would you like to join the waiting list?"

        result = self.warning_prompt_helper.evaluate_alert(
            mock_alert, prioritize_waiting_list=True
        )
        self.assertTrue(result)

    # def test_evaluate_alert_cancel_booking(self):
    #     mock_alert = MagicMock()
    #     mock_alert.text = "Möchtest du deine Buchung wirklich stornieren?"

    #     result = self.warning_prompt_helper.evaluate_alert(mock_alert, prioritize_waiting_list=False)
    #     self.assertTrue(result)

    # def test_evaluate_alert_not_identified(self):
    #     mock_alert = MagicMock()
    #     mock_alert.text = "Some unknown alert message"

    #     result = self.warning_prompt_helper.evaluate_alert(mock_alert, prioritize_waiting_list=False)
    #     self.assertEqual(result, AlertTypes.NotIdentifyAlert)

    @patch("selenium.webdriver.support.ui.WebDriverWait.until")
    def test_error_is_present(self, mock_wait):
        mock_error_window = MagicMock()
        mock_wait.return_value = mock_error_window
        self.driver.find_element.return_value.text = (
            "You have reached your maximum bookings per day limit"
        )

        error_text = self.warning_prompt_helper.error_is_present()
        self.assertIsNotNone(error_text)
        self.assertEqual(
            error_text, "You have reached your maximum bookings per day limit"
        )

    @patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        side_effect=TimeoutException,
    )
    def test_error_is_not_present(self, mock_wait):
        error_text = self.warning_prompt_helper.error_is_present()
        self.assertIsNone(error_text)

    def test_evaluate_error_max_bookings(self):
        result = self.warning_prompt_helper.evaluate_error(AlertTypes.MaxBookings.value)
        self.assertTrue(result)

    def test_evaluate_error_class_full(self):
        result = self.warning_prompt_helper.evaluate_error(AlertTypes.ClassFull.value)
        self.assertFalse(result)

    def test_evaluate_error_not_identified(self):
        result = self.warning_prompt_helper.evaluate_error("Some unknown error message")
        self.assertFalse(result)

    @patch("selenium.webdriver.support.ui.WebDriverWait.until")
    def test_login_error_is_present(self, mock_wait):
        mock_alert_div = MagicMock()
        mock_alert_div.text = "The user credentials were incorrect."
        mock_wait.return_value = mock_alert_div

        result = self.warning_prompt_helper.login_error_is_present()
        self.assertTrue(result)

    @patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        side_effect=TimeoutException,
    )
    def test_login_error_is_not_present(self, mock_wait):
        result = self.warning_prompt_helper.login_error_is_present()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
