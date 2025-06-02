from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    SessionNotCreatedException,
    NoSuchDriverException,
)
import logging


class WebDriverManager:
    def __init__(self, chromedriver: str, env: str = "prd"):
        """Initializes the WebDriverManager with the given ChromeDriver path and environment.

        Args:
            chromedriver (str): location of the ChromeDriver.
            env (str): environment ("prd" for production or "dev" for development).
        """
        self.chromedriver = chromedriver
        self.env = env
        self.driver = self.set_driver()  # Initialize the driver

    def set_driver(self) -> webdriver.Chrome:
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
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
        except (SessionNotCreatedException, NoSuchDriverException) as e:
            logging.warning(
                "Failed to create a WebDriver session. Please check the ChromeDriver path and ensure it is compatible with your Chrome version."
            )
            logging.error(e, exc_info=True)
            raise ValueError(
                "Failed to create a WebDriver session. Please check the ChromeDriver path and ensure it is compatible with your Chrome version."
            )
        return self.driver

    def close_driver(self) -> None:
        """Closes the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_driver(self):
        return self.driver
