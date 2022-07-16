from selenium import webdriver


def get_driver(chromedriver: str) -> object:
    """Sets the Google ChromeDriver with headless support enabled

    Args:
        chromedriver (str): location of the ChromeDriver

    Returns:
        object: Driver Object Selenium can work on
    """
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(chrome_options=options, executable_path=chromedriver)
    return driver


def close_driver(driver: object) -> None:
    """Closes the Webdriver

    Args:
        driver (object): Webdriver to be closed
    """
    driver.close()
