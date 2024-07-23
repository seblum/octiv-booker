from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .webdriver_manager import WebDriverManager

class SeleniumManager(WebDriverManager):
    def __init__(self, chromedriver: str, env: str = "prd"):
        super().__init__(chromedriver=chromedriver, env=env)

    def input_text(self, xpath: str, text: str) -> None:
        WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, xpath))
        ).send_keys(text)

    def click_button(self, xpath: str) -> None:
        WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, xpath))
        ).click()

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def execute_script(self, script, element):
        self.driver.execute_script(script, element)

    def wait_for_element(self, by: By, value: str, timeout=20):
        condition = ec.presence_of_element_located((by, value))
        return WebDriverWait(self.driver, timeout).until(condition)

    def wait_for_element_by_xpath(self, xpath: str, timeout=20):
        condition = ec.presence_of_element_located((By.XPATH, xpath))
        return WebDriverWait(self.driver, timeout).until(condition)

    def wait_for_element_with_message(self, condition, timeout=3, error_message=""):
        try:
            return WebDriverWait(self.driver, timeout).until(condition, error_message)
        except (TimeoutException, NoSuchElementException):
            return None
        
    def wait_for_element_presence(self, xpath):
        return self.wait_for_element_with_message(condition=ec.presence_of_element_located(
            (By.XPATH, xpath)
        ))
        
    def wait_for_element_presence_alert(self):
        return self.wait_for_element_with_message(condition=ec.alert_is_present(),
            error_message="Timed out waiting for alert to appear.")
    
    def wait_for_element_to_be_clickable_by_xpath(self, xpath):
        WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, xpath))
        )

    def get_page(self, base_url) -> None:
        self.driver.get(base_url)

    def switch_to_alert(self) -> None:
        self.driver.switch_to.alert

    def find_element_by_xpath(self, xpath: str):
        return self.driver.find_element(By.XPATH, xpath)

    def find_elements_by_xpath(self, xpath: str):
        return self.driver.find_elements(By.XPATH, xpath)

    def get_element_text_by_xpath(self, xpath: str) -> str:
        element = self.find_element_by_xpath(xpath)
        return element.text

