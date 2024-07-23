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

    def get_driver(self):
        return self.driver
