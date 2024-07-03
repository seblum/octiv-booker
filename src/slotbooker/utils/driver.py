from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_driver(chromedriver: str, env: str = "prd") -> object:
    """Sets the Google ChromeDriver with headless support enabled

    Args:
        chromedriver (str): location of the ChromeDriver

    Returns:
        object: Driver Object Selenium can work on
    """
    service = Service(executable_path=chromedriver)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("detach", True)
    if env != "dev":
        options.add_argument("--headless")  # needs to be set to run in docker image

    # added for lambda | if run locally not working.
    # options.add_argument("--window-size=1280x1696")
    # options.add_argument("--single-process")
    # options.add_argument("--disable-dev-tools")
    # options.add_argument("--no-zygote")
    # options.add_argument("--incognito")
    # options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=service, options=options)

    return driver


def close_driver(driver: object) -> None:
    """Closes the Webdriver

    Args:
        driver (object): Webdriver to be closed
    """
    driver.close()
