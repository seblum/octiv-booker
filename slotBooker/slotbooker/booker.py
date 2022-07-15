import os

import yaml

from .driver import close_driver, get_driver
from .ui_interaction import book_slot, login, switch_day

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))

# insert main function
def main():
    driver = get_driver(chromedriver=config.get("chromedriver"))

    login(driver, base_url=config.get("base_url"), username=config.get("email"), password=config.get("password"))

    day = switch_day(driver, days_before_bookable=config.get("days_before_bookable"))

    book_slot(
        driver,  # depending on day, select class
        class_name=config.get("class").get(day),
        book_action=config.get("book_class"),
    )

    close_driver(driver)


if __name__ == "__main__":
    main()
