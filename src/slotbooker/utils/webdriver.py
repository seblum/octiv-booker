from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

class WebDriverManager:
    def __init__(self, chromedriver: str, env: str = "prd"):
        """Initializes the WebDriverManager with the given ChromeDriver path and environment.

        Args:
            chromedriver (str): location of the ChromeDriver.
            env (str): environment ("prd" for production or "dev" for development).
        """
        self.chromedriver = chromedriver
        self.env = env
        self.driver = self.get_driver()  # Initialize the driver

    def get_driver(self) -> webdriver.Chrome:
        """Sets the Google ChromeDriver with headless support enabled if not in development environment.

        Returns:
            webdriver.Chrome: Driver Object Selenium can work on.
        """
        service = Service(executable_path=self.chromedriver)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("detach", True)
        if self.env != "dev":
            options.add_argument("--headless")  # needs to be set to run in docker image

        # added for lambda | if run locally not working.
        # options.add_argument("--window-size=1280x1696")
        # options.add_argument("--single-process")
        # options.add_argument("--disable-dev-tools")
        # options.add_argument("--no-zygote")
        # options.add_argument("--incognito")
        # options.add_argument("--remote-debugging-port=9222")

        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def close_driver(self) -> None:
        """Closes the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_page(self,base_url) -> None:
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

    def wait_for_element(self, by: By, value: str, timeout=20):
        condition = ec.presence_of_element_located((by, value))
        return WebDriverWait(self.driver, timeout).until(condition)

    def wait_for_elementt_by_xpath(self, value: str, timeout=20):
        condition = ec.presence_of_element_located((By.XPATH, value))
        return WebDriverWait(self.driver, timeout).until(condition)

    def input_text(self, xpath: str, text: str) -> None:
        WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, xpath))
        ).send_keys(text)

    def click_button(self, xpath: str) -> None:
        WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, xpath))
        ).click()

    def execute_script(self, script, element) -> None:
        self.driver.execute_script(script, element)

    def wait_for_element_to_be_clickable_by_xpath(self,xpath):
        WebDriverWait(self.driver, 20).until(
                ec.element_to_be_clickable(
                    (By.XPATH, xpath)
                )
            )