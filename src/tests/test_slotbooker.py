from unittest.mock import patch, MagicMock
from datetime import datetime
from slotbooker.slotbooker import Booker  # Update import as per your actual structure
import pytest


@patch("slotbooker.slotbooker.XPath")
@patch("slotbooker.slotbooker.AlertErrorHandler.check_login_alert")
@patch("slotbooker.slotbooker.SeleniumManager")
def test_login_successful(mock_selenium_manager, mock_check_alert, mock_xpath):
    # Mock dependencies
    mock_selenium = MagicMock()
    mock_selenium.driver_is_initialialized.return_value = True
    mock_selenium.get_page.return_value = None
    mock_selenium.input_text.return_value = None
    mock_selenium.click_button.return_value = None
    mock_selenium_manager.return_value = mock_selenium

    # Mock XPath returns
    mock_xpath.login_username_input.return_value = "xpath_username_input"
    mock_xpath.login_username_button.return_value = "xpath_username_button"
    mock_xpath.login_password_input.return_value = "xpath_password_input"
    mock_xpath.login_password_check.return_value = "xpath_password_check"
    mock_xpath.login_password_button.return_value = "xpath_password_button"

    # Mock AlertErrorHandler
    mock_check_alert.return_value = False

    # Instantiate and call
    booker = Booker(base_url="http://example.com")
    result = booker.login("testuser", "testpass")

    # Assertions
    assert result is True
    mock_selenium.get_page.assert_called_once_with(base_url="http://example.com")
    mock_selenium.input_text.assert_any_call("xpath_username_input", "testuser")
    mock_selenium.input_text.assert_any_call("xpath_password_input", "testpass")
    mock_check_alert.assert_called_once_with(selenium_manager=mock_selenium)


@patch("slotbooker.slotbooker.XPath")
@patch("slotbooker.slotbooker.AlertErrorHandler.check_login_alert")
@patch("slotbooker.slotbooker.SeleniumManager")
def test_login_triggers_stop_booking(
    mock_selenium_manager, mock_check_alert, mock_xpath
):
    # Mock setup as before
    mock_selenium = MagicMock()
    mock_selenium.driver_is_initialialized.return_value = True
    mock_selenium_manager.return_value = mock_selenium

    mock_xpath.login_username_input.return_value = "xpath_username_input"
    mock_xpath.login_username_button.return_value = "xpath_username_button"
    mock_xpath.login_password_input.return_value = "xpath_password_input"
    mock_xpath.login_password_check.return_value = "xpath_password_check"
    mock_xpath.login_password_button.return_value = "xpath_password_button"

    mock_check_alert.return_value = True  # Simulate stop condition

    # Patch __continue_booking to return True without side effects
    with patch.object(Booker, "_Booker__stop_booking", return_value=False) as mock_stop:
        booker = Booker(base_url="http://example.com")
        result = booker.login("testuser", "testpass")
        assert result is False
        mock_stop.assert_called_once()


@patch("slotbooker.slotbooker.get_day")
@patch("slotbooker.slotbooker.XPath")
@patch("slotbooker.slotbooker.os.environ", {"DAYS_BEFORE_BOOKABLE": "3"})
def test_switch_day_success(mock_xpath, mock_get_day):
    # Arrange mocks
    mock_xpath.switch_week_button.return_value = "xpath_switch_week"
    mock_xpath.weekday_button.return_value = "xpath_day_button"
    mock_get_day.return_value = (datetime(2025, 6, 10), 2)  # Tuesday, 2 weeks diff

    booker = Booker(base_url="http://example.com")
    booker.selenium_manager = MagicMock()
    booker.selenium_manager.driver_is_initialialized.return_value = True
    booker.selenium_manager.click_button.return_value = None

    # Act
    day, date_str = booker.switch_day()

    # Assert
    assert day == "Tuesday"
    assert date_str == "10/06/2025"
    assert booker.day == "Tuesday"
    assert booker.booking_information["current_date"] == "Tuesday, 10/06/2025"

    # Should call click_button 2 times for weeks and once for the day
    assert booker.selenium_manager.click_button.call_count == 3
    booker.selenium_manager.click_button.assert_any_call("xpath_switch_week")
    booker.selenium_manager.click_button.assert_any_call("xpath_day_button")


@patch("slotbooker.slotbooker.get_day")
@patch("slotbooker.slotbooker.XPath")
def test_switch_day_raises_exception_and_calls_stop_booking(mock_xpath, mock_get_day):
    mock_get_day.return_value = (datetime(2025, 6, 10), 1)
    mock_xpath.switch_week_button.return_value = "xpath_switch_week"
    mock_xpath.weekday_button.return_value = "xpath_day_button"

    booker = Booker(base_url="http://example.com")
    booker.selenium_manager = MagicMock()
    booker.selenium_manager.driver_is_initialialized.return_value = True

    # Simulate exception on click_button when clicking the weekday button
    def click_button_side_effect(arg):
        if arg == "xpath_day_button":
            raise Exception("Click failed")
        return None

    booker.selenium_manager.click_button.side_effect = click_button_side_effect

    # Patch __stop_booking method to spy on it
    with patch.object(
        booker, "_Booker__stop_booking", wraps=booker._Booker__stop_booking
    ) as mock_stop_booking:
        with pytest.raises(Exception) as excinfo:
            booker.switch_day()

        assert "Click failed" in str(excinfo.value)
        mock_stop_booking.assert_called_once()
