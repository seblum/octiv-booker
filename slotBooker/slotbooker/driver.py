from selenium import webdriver



def get_driver(chromedriver: str) -> object:
    # add headless support
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(chrome_options=options, executable_path=chromedriver)
    return driver


def close_driver(driver: object) -> None:
    driver.close()