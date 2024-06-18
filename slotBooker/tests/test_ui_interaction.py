from slotbooker import __version__

def test_version():
    assert __version__ == "0.1.0"


import pytest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By
from slotbooker.ui_interaction import Booker

@pytest.fixture
def mock_driver():
    return MagicMock()

@pytest.fixture
def booker(mock_driver):
    return Booker(
        driver=mock_driver,
        base_url="https://example.com",
        days_before_bookable=7,
        execution_booking_time="10:00:00.000000"
    )

def test_login(booker, mock_driver):
    username = "testuser"
    password = "password"

    booker.login(username, password)

    mock_driver.get.assert_called_once_with("https://example.com")
    assert mock_driver.find_element.call_count == 3
    assert mock_driver.find_element.return_value.send_keys.call_count == 2
    assert mock_driver.find_element.return_value.click.call_count == 3

def test_switch_day(booker, mock_driver):
    mock_driver.find_element.return_value.text = "Mocked Text"
    
    with patch("booker_module.get_day", return_value=(datetime(2022, 1, 10), 1)):
        with patch("booker_module.get_day_button", return_value="mocked_xpath"):
            booker.switch_day()

            assert mock_driver.find_element.call_count == 1
            mock_driver.find_element.return_value.click.assert_called_once()

def test_book_class(booker, mock_driver):
    class_dict = {
        "Monday": [
            {"time": "10:00", "class": "Yoga", "wl": False},
            {"time": "11:00", "class": "Pilates", "wl": True}
        ]
    }

    booker.class_dict = class_dict
    booker.day = "Monday"

    mock_driver.find_elements.return_value = ["MockElement"]
    with patch("booker_module.get_booking_slot", return_value="mocked_xpath"):
        booker.book_class(class_dict)

        assert mock_driver.find_elements.call_count == 1
        assert mock_driver.find_element.call_count == 2

def test_input_text(booker, mock_driver):
    xpath = "mock_xpath"
    text = "mock_text"

    booker._input_text(xpath, text)
    mock_driver.find_element.assert_called_once_with(By.XPATH, xpath)
    mock_driver.find_element.return_value.send_keys.assert_called_once_with(text)

def test_click_button(booker, mock_driver):
    xpath = "mock_xpath"

    booker._click_button(xpath)
    mock_driver.find_element.assert_called_once_with(By.XPATH, xpath)
    mock_driver.find_element.return_value.click.assert_called_once()
