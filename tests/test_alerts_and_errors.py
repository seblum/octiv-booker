import pytest
from unittest.mock import MagicMock
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.alerts_and_errors import (
    alert_is_present,
    evaluate_alert,
    error_is_present,
    evaluate_error,
    AlertTypes,
    continue_bookings,
    stop_booking_process
)

def test_alert_is_present_no_alert(mocker):
    driver = MagicMock()
    mocker.patch('selenium.webdriver.support.ui.WebDriverWait.until', side_effect=TimeoutException)
    assert alert_is_present(driver) is None

def test_alert_is_present_with_alert(mocker):
    driver = MagicMock()
    mock_alert = MagicMock()
    driver.switch_to.alert = mock_alert
    mocker.patch('selenium.webdriver.support.ui.WebDriverWait.until', return_value=True)
    assert alert_is_present(driver) == mock_alert

@pytest.mark.parametrize("alert_text, prioritize_waiting_list, expected", [
    ("waiting list", True, stop_booking_process()),
    ("waiting list", False, continue_bookings()),
    ("wirklich stornieren?", False, continue_bookings()),
    ("unexpected alert text", False, continue_bookings()),
])
def test_evaluate_alert(alert_text, prioritize_waiting_list, expected, mocker):
    alert_obj = MagicMock()
    alert_obj.text = alert_text

    if alert_text == "waiting list":
        mocker.patch('your_module._handle_waiting_list_booking', return_value=expected)
    elif alert_text == "wirklich stornieren?":
        mocker.patch('your_module._handle_cancel_slot', return_value=expected)
    else:
        mocker.patch('your_module.continue_bookings', return_value=expected)

    result = evaluate_alert(alert_obj, prioritize_waiting_list)
    assert result == expected

def test_error_is_present_no_error(mocker):
    driver = MagicMock()
    mocker.patch.object(driver, 'find_element', side_effect=NoSuchElementException)
    assert error_is_present(driver) is None

def test_error_is_present_with_error():
    driver = MagicMock()
    error_text = "Some error occurred"
    mock_element = MagicMock()
    mock_element.text = error_text
    driver.find_element.return_value = mock_element
    assert error_is_present(driver) == error_text

@pytest.mark.parametrize("error_text, expected", [
    (AlertTypes.MaxBookings.value, True),
    (AlertTypes.CannotBookInAdvance.value, True),
    (AlertTypes.ClassFull.value, False),
    ("Some unexpected error", False),
])
def test_evaluate_error(error_text, expected):
    assert evaluate_error(error_text) == expected
