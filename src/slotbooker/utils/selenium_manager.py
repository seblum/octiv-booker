from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .webdriver_manager import WebDriverManager


class SeleniumManager(WebDriverManager):
    def __init__(self, chromedriver: str, env: str = "prd"):
        super().__init__(chromedriver=chromedriver, env=env)

    def wait_for_element(
        self,
        by=By.XPATH,
        xpath=None,
        timeout=20,
        condition=ec.presence_of_element_located,
        error_message="",
    ):
        try:
            return WebDriverWait(self.driver, timeout).until(
                condition((by, xpath)), error_message
            )
        except (TimeoutException, NoSuchElementException):
            return None

    def wait_for_element_alert(self):
        try:
            return WebDriverWait(self.driver, timeout=5).until(
                ec.alert_is_present(), "Timed out waiting for alert to appear."
            )
        except (TimeoutException, NoSuchElementException):
            return None

    def input_text(self, xpath: str, text: str) -> None:
        element = self.wait_for_element(
            xpath=xpath, condition=ec.element_to_be_clickable
        )
        if element:
            element.send_keys(text)

    def click_button(self, xpath: str) -> None:
        element = self.wait_for_element(
            xpath=xpath, condition=ec.element_to_be_clickable
        )
        if element:
            element.click()

    def find_element(self, by=By.XPATH, xpath=None):
        return self.driver.find_element(by, xpath)

    def find_elements(self, by=By.XPATH, xpath=None):
        return self.driver.find_elements(by, xpath)

    def execute_script(self, script, element):
        self.driver.execute_script(script, element)

    def get_page(self, base_url) -> None:
        self.driver.get(base_url)

    def switch_to_alert(self) -> None:
        self.driver.switch_to.alert

    def get_element_text(self, by=By.XPATH, xpath: str = None) -> str:
        element = self.find_element(by, xpath)
        return element.text
