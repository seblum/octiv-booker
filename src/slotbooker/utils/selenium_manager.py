import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as exco
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from .webdriver_manager import WebDriverManager

class SeleniumManager(WebDriverManager):

    def __init__(self, chromedriver: str, env: str = "prd"):
        super().__init__(chromedriver=chromedriver, env=env)

    def input_text(self, xpath: str, text: str) -> None:
        WebDriverWait(self.driver, 20).until(
            exco.element_to_be_clickable((By.XPATH, xpath))
        ).send_keys(text)

    def click_button(self, xpath: str) -> None:
        WebDriverWait(self.driver, 20).until(
            exco.element_to_be_clickable((By.XPATH, xpath))
        ).click()

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def execute_script(self, script, element):
        self.driver.execute_script(script, element)

    def wait_for_element(self, condition, timeout=20):
        return WebDriverWait(self.driver, timeout).until(condition)

    def close_driver(self):
        self.driver.quit()
