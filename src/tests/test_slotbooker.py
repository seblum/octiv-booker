from unittest.mock import patch, MagicMock
from datetime import datetime
from slotbooker.slotbooker import Booker  # Update import as per your actual structure


@patch("slotbooker.slotbooker.get_day")
@patch("slotbooker.slotbooker.XPath")
@patch("slotbooker.slotbooker.SeleniumManager")
def test_switch_day(mock_selenium_manager, mock_xpath, mock_get_day, monkeypatch):
    # Setup mock environment
    monkeypatch.setenv("DAYS_BEFORE_BOOKABLE", "3")

    mock_selenium = MagicMock()
    mock_selenium.driver_is_initialialized.return_value = True
    mock_selenium.click_button.return_value = None
    mock_selenium_manager.return_value = mock_selenium

    # Setup get_day to return a known day
    test_date = datetime(2025, 6, 10)  # Let's say it's a Tuesday
    mock_get_day.return_value = (test_date, 2)

    # Mock XPath methods
    mock_xpath.switch_week_button.return_value = "xpath_to_week_button"
    mock_xpath.weekday_button.return_value = "xpath_to_tuesday_button"

    # Instantiate Booker and run switch_day
    booker = Booker(base_url="http://example.com")
    day, date_str = booker.switch_day()

    # Assertions
    assert day == "Tuesday"
    assert date_str == "10/06/2025"
    assert booker.day == "Tuesday"
    assert booker.booking_information["current_date"] == "Tuesday, 10/06/2025"

    # Check that switching weeks happened
    assert mock_selenium.click_button.call_count == 3  # 2 for week switch, 1 for day
    mock_selenium.click_button.assert_any_call("xpath_to_week_button")
    mock_selenium.click_button.assert_any_call("xpath_to_tuesday_button")


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
