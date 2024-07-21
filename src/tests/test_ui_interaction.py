import unittest
from unittest.mock import Mock, patch

from slotbooker.booker import Booker


class TestBooker(unittest.TestCase):
    def setUp(self):
        self.driver = Mock()
        self.base_url = "http://example.com"
        self.days_before_bookable = 3
        self.execution_booking_time = "09:00:00.000000"
        self.booker = Booker(
            self.driver,
            self.base_url,
            self.days_before_bookable,
            self.execution_booking_time,
        )
        self.username = "user"
        self.password = "pass"
        self.class_dict = {"Monday": [{"class": "Yoga", "time": "10:00", "wl": True}]}
        self.booker.class_dict = self.class_dict

    # @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    # def test_switch_day(self, mock_wait_until):
    #     self.booker.switch_day()
    #     calls = [
    #         call((By.XPATH, self.booker.xpath_helper.get_xpath_booking_head() + "[3]/div[9]/div/div/i")),
    #         call((By.XPATH, self.booker.booking_helper.get_day_button("Monday", self.booker.xpath_helper)))
    #     ]
    #     mock_wait_until.assert_has_calls(calls, any_order=True)

    # @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    # @patch('selenium.webdriver.remote.webdriver.WebDriver.find_elements')
    # def test_book_class(self, mock_find_elements, mock_wait_until):
    #     slot_element = Mock()
    #     mock_find_elements.return_value = [slot_element]
    #     mock_wait_until.return_value = slot_element
    #     self.booker.book_class(self.class_dict)
    #     mock_find_elements.assert_called_with(By.XPATH, self.booker.xpath_helper.get_xpath_booking_head())

    # @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    # @patch('selenium.webdriver.remote.webdriver.WebDriver.find_elements')
    # def test_book_class_with_no_class(self, mock_find_elements, mock_wait_until):
    #     self.class_dict = {"Monday": [{"class": "None", "time": "10:00", "wl": True}]}
    #     self.booker.class_dict = self.class_dict
    #     slot_element = Mock()
    #     mock_find_elements.return_value = [slot_element]
    #     mock_wait_until.return_value = slot_element
    #     self.booker.book_class(self.class_dict)
    #     self.assertFalse(mock_find_elements.called)

    @patch("selenium.webdriver.support.ui.WebDriverWait.until")
    def test_input_text(self, mock_wait_until):
        element = Mock()
        mock_wait_until.return_value = element
        xpath = "/some/xpath"
        text = "some text"
        self.booker._input_text(xpath, text)
        element.send_keys.assert_called_with(text)

    @patch("selenium.webdriver.support.ui.WebDriverWait.until")
    def test_click_button(self, mock_wait_until):
        element = Mock()
        mock_wait_until.return_value = element
        xpath = "/some/xpath"
        self.booker._click_button(xpath)
        element.click.assert_called()

    # def test_load_and_transform_input_class_dict(self):
    #     transformed_list = self.booker._load_and_transform_input_class_dict()
    #     self.assertEqual(transformed_list, ["Yoga"])

    # @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    # @patch('selenium.webdriver.remote.webdriver.WebDriver.find_elements')
    # def test_get_all_bounding_boxes_in_window(self, mock_find_elements, mock_wait_until):
    #     element = Mock()
    #     mock_find_elements.return_value = [element]
    #     result = self.booker._get_all_bounding_boxes_in_window()
    #     self.assertEqual(result, [element])
    #     mock_wait_until.assert_called_with(
    #         exco.element_to_be_clickable((By.XPATH, self.booker.xpath_helper.get_xpath_booking_head()))
    #     )

    # @patch('selenium.webdriver.remote.webdriver.WebDriver.find_element')
    # def test_get_all_bounding_boxes_by_class_name(self, mock_find_element):
    #     slot_element = Mock()
    #     slot_element.text = "Yoga"
    #     mock_find_element.side_effect = [slot_element, slot_element]
    #     class_entry_list = ["Yoga"]
    #     all_slots_bounding_boxes = [slot_element]
    #     result = self.booker._get_all_bounding_boxes_by_class_name(class_entry_list, all_slots_bounding_boxes)
    #     expected_xpath = self.booker.xpath_helper.get_xpath_booking_slot(1, True)
    #     self.assertEqual(
    #         result,
    #         defaultdict(
    #             list,
    #             {
    #                 "Yoga": [
    #                     {
    #                         "10:00": {
    #                             "textfield": "Yoga",
    #                             "time_slot": "10:00",
    #                             "slot_index": 1,
    #                             "xpath": expected_xpath,
    #                         }
    #                     }
    #                 ]
    #             }
    #         )
    #     )

    def test_get_button_xpath(self):
        all_possible_booking_slots_dict = {
            "Yoga": [
                {
                    "10:00": {
                        "textfield": "Yoga",
                        "time_slot": "10:00",
                        "slot_index": 1,
                        "xpath": "/some/xpath",
                    }
                }
            ]
        }
        result = self.booker._get_button_xpath(all_possible_booking_slots_dict)
        self.assertEqual(result, "/some/xpath")

    # @patch('selenium.webdriver.remote.webdriver.WebDriver.find_element')
    # @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    # def test_check_login_alert(self, mock_wait_until, mock_find_element):
    #     element = Mock()
    #     element.text = "Invalid credentials"
    #     mock_wait_until.return_value = element
    #     result = self.booker._check_login_alert()
    #     self.assertEqual(result, "Invalid credentials")
    #     mock_wait_until.assert_called_with(
    #         exco.presence_of_element_located(
    #             (By.XPATH, self.booker.xpath_helper.get_xpath_login_error_window())
    #         )
    #     )


if __name__ == "__main__":
    unittest.main()
