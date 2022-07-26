import os

import yaml
from driver import close_driver, get_driver
from ui_interaction import book_slot, login, switch_day

# Load config yaml
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))


def main():
    """Main of Slotbooker. Gets driver, logs into website, selects
    the day wanted, and books slot. Closes driver afterwards
    """
    # get env variables
    USER = os.environ.get("OCTIV_USERNAME")
    PASSWORD = os.environ.get("OCTIV_PASSWORD")

    # check whether env variables are set or None
    if USER is None or PASSWORD is None:
        print("USERNAME and PASSWORD not set")
        print("Please run 'source set-credentials.sh' to set env variables")
    else:
        driver = get_driver(chromedriver=config.get("chromedriver"))

        login(driver, base_url=config.get("base_url"), username=USER, password=PASSWORD)

        day = switch_day(driver, days_before_bookable=config.get("days_before_bookable"))

        book_slot(
            driver,
            class_name=config.get("class").get(day),  # depending on day, select class
            booking_action=config.get("book_class"),
        )

        close_driver(driver)


if __name__ == "__main__":
    main()
