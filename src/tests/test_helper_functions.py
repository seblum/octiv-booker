import pytest
from datetime import date, timedelta
from slotbooker.helper_functions import (
    get_xpath_booking_head,
    get_xpath_login_username_head,
    get_xpath_login_password_head,
    get_day,
    get_day_button,
    get_booking_slot,
    get_error_window,
    get_error_text_window,
    continue_bookings,
    stop_booking_process
)

def test_get_xpath_booking_head():
    assert get_xpath_booking_head() == "/html/body/div/div[6]/div/div"

def test_get_xpath_login_username_head():
    assert get_xpath_login_username_head() == "/html/body/div/div[3]/div/div/div/div/div/div/form"

def test_get_xpath_login_password_head():
    assert get_xpath_login_password_head() == "/html/body/div[1]/div[3]/div/div/div/div/div/div/form"

def test_get_day():
    today = date.today()
    future_date, diff_week = get_day(5)
    expected_future_date = today + timedelta(days=5)
    expected_diff_week = expected_future_date.isocalendar().week - today.isocalendar().week
    assert future_date == expected_future_date
    assert diff_week == expected_diff_week

@pytest.mark.parametrize("day_to_book, expected_xpath", [
    ("Monday", f"{get_xpath_booking_head()}[3]/div[2]/div/p"),
    ("Tuesday", f"{get_xpath_booking_head()}[3]/div[3]/div/p"),
    ("Wednesday", f"{get_xpath_booking_head()}[3]/div[4]/div/p"),
    ("Thursday", f"{get_xpath_booking_head()}[3]/div[5]/div/p"),
    ("Friday", f"{get_xpath_booking_head()}[3]/div[6]/div/p"),
    ("Saturday", f"{get_xpath_booking_head()}[3]/div[7]/div/p"),
    ("Sunday", f"{get_xpath_booking_head()}[3]/div[8]/div/p"),
])
def test_get_day_button(day_to_book, expected_xpath):
    assert get_day_button(day_to_book) == expected_xpath

@pytest.mark.parametrize("booking_slot, book_action, expected_xpath", [
    (1, True, f"{get_xpath_booking_head()}[1]/div/div[1]/div[3]/button"),
    (1, False, f"{get_xpath_booking_head()}[1]/div/div[2]/div[3]/button"),
    (2, True, f"{get_xpath_booking_head()}[2]/div/div[1]/div[3]/button"),
    (2, False, f"{get_xpath_booking_head()}[2]/div/div[2]/div[3]/button"),
])
def test_get_booking_slot(booking_slot, book_action, expected_xpath):
    assert get_booking_slot(booking_slot, book_action) == expected_xpath

def test_get_error_window():
    assert get_error_window() == "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[1]"

def test_get_error_text_window():
    assert get_error_text_window() == "/html/body/div/div[2]/div/div/div[1]/div/div/div[2]/p[2]"

def test_continue_bookings():
    assert continue_bookings() is False

def test_stop_booking_process():
    assert stop_booking_process() is True
